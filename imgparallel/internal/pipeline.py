"""
input dataset --> stages of processing --> output dataset
- Understand input dataset structure
- In parallel:
    - Copy over metadata and other files if necessary
    - Read images, process them, write them (run pipeline on image paths)
"""

import cv2
import os
import multiprocessing as mp
from typing import List, Any
from numpy.typing import NDArray
from imgparallel.internal.dataset import Dataset, Sample
from imgparallel.internal.file_io import (
    read_image_from_path,
    write_image_to_path,
    check_permissions,
)


class Stage:

    def __init__(self) -> None:
        pass

    def setup(self, process_index: int, total_process_count: int) -> None:
        pass

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError


class InputStage(Stage):

    def __init__(self, dataset: Dataset) -> None:
        super().__init__()
        self.dataset = dataset
        self.dataset_iter = None
        self.failure_count = 0

    def setup(self, process_index: int, total_process_count: int) -> None:
        self.dataset_iter = self.dataset.iter_partitioned(process_index, total_process_count)

    def __call__(self) -> Any:
        if self.dataset_iter is None:
            raise RuntimeError("InputStage has not been setup before attempting to run!")

        sample = None
        while sample is None:
            sample = next(self.dataset_iter)
            try:
                sample.data = read_image_from_path(sample.full_path)
            except FileNotFoundError:
                self.failure_count += 1
                print(f"Failed to read {sample.full_path}")
                sample = None

        return sample


class ResizeStage(Stage):

    def __init__(self, target_width, target_height) -> None:
        super().__init__()
        self.target_width = target_width
        self.target_height = target_height

    def __call__(self, sample: Sample) -> Any:
        if sample.data is None:
            raise ValueError("There is no image data to resize!")
        sample.data = cv2.resize(sample.data, (self.target_width, self.target_height))
        return sample


class OutputStage(Stage):

    def __init__(self, dataset: Dataset) -> None:
        super().__init__()
        self.dataset = dataset

    def __call__(self, sample: Sample) -> Any:
        if sample.data is None:
            raise ValueError("There is no image data to write!")
        output_path = self.dataset.get_output_path_for_sample(sample)
        write_image_to_path(output_path, sample.data)


def worker(input_queue, output_queue, stage, proc_idx, num_proc):
    # Setup the stage with information about this process and the pool
    stage.setup(proc_idx, num_proc)

    while True:
        if input_queue:
            sample = input_queue.get()
            if sample is None:  # Poison pill to shutdown
                if output_queue:
                    output_queue.put(None)  # Propagate shutdown signal
                break

            processed_sample = stage(sample)
            if output_queue:
                output_queue.put(processed_sample)
        else:
            # Input stages have no input queue
            try:
                sample = stage()
            except StopIteration:
                output_queue.put(None)  # Insert poison pill to shutdown
                break

            if output_queue:
                output_queue.put(sample)


class Pipeline:

    def __init__(self) -> None:
        self.stages: List[Stage] = []
        self.queues: List[mp.Queue] = []

    def read_images(self, dataset: Dataset) -> "Pipeline":
        self.stages.append(InputStage(dataset))
        return self

    def resize(self, width: int = -1, height: int = -1) -> "Pipeline":
        if width == -1 or height == -1:
            return self

        self.stages.append(ResizeStage(width, height))
        return self

    def write_images(self, dataset: Dataset) -> "Pipeline":
        self.stages.append(OutputStage(dataset))
        return self

    def sanity_check(self):
        if not isinstance(self.stages[0], InputStage):
            raise RuntimeError("Pipeline does not begin with an InputStage!")

        if not isinstance(self.stages[-1], OutputStage):
            raise RuntimeError("Pipeline does not end with an OutputStage!")

        os.makedirs(self.stages[-1].dataset.root_dir, exist_ok=True)

        if not check_permissions(self.stages[-1].dataset.root_dir):
            raise PermissionError("Cannot write to output dataset root directory!")

    def run(self, num_processes_per_stage=1):
        self.sanity_check()

        # List to keep track of processes for clean shutdown
        processes = []
        self.queues = [mp.Queue() for _ in range(len(self.stages) - 1)]

        # Setup all processes for each stage
        for i, stage in enumerate(self.stages):
            for p_idx in range(num_processes_per_stage):
                in_queue = self.queues[i - 1] if i > 0 else None
                out_queue = self.queues[i] if i < len(self.queues) else None
                p = mp.Process(
                    target=worker, args=(in_queue, out_queue, stage, p_idx, num_processes_per_stage)
                )
                p.start()
                processes.append(p)

        # Ensure all processes complete
        for p in processes:
            p.join()
