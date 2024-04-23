"""
Classes for handling the structure of datasets stored on disk.
"""

import os
import mimetypes
from dataclasses import dataclass
from typing import Iterator, Dict, Any


# TODO: would this be better if Sample stored root_dir and relative_path instead of full_path?
@dataclass
class Sample:
    full_path: str
    relative_path: str
    data: Any = None
    metadata: Dict[str, Any] = None


class Dataset:
    def __init__(self, root_dir: str, output_format: str = None) -> None:
        self.root_dir = os.path.abspath(root_dir)
        self.output_format = output_format

    def iter_partitioned(self, partition_index, total_partitions):
        return self._scan_directory(partition_index, total_partitions)

    def __iter__(self) -> Iterator[Sample]:
        """Make the dataset class iterable, yielding samples as needed."""
        return self._scan_directory(0, 1)

    def _scan_directory(self, partition_index, total_partitions) -> Iterator[Sample]:
        supported_images = ["image/jpeg", "image/png", "image/gif", "image/bmp", "image/tiff"]
        file_list = []
        for root, dirs, files in os.walk(self.root_dir):
            for file in files:
                file_path = os.path.join(root, file)
                mime_type, _ = mimetypes.guess_type(file_path)
                if mime_type in supported_images:
                    file_list.append(file_path)

        # Split the file list into partitions
        if total_partitions > 1:
            partition_size = len(file_list) // total_partitions
            start_index = partition_index * partition_size
            end_index = (
                start_index + partition_size
                if partition_index < total_partitions - 1
                else len(file_list)
            )

            file_list = file_list[start_index:end_index]

        for file_path in file_list:
            yield Sample(
                full_path=file_path, relative_path=os.path.relpath(file_path, start=self.root_dir)
            )

    def moved_to(self, new_root_dir: str) -> "Dataset":
        """Update the base directory for output."""
        # This method will create a new Dataset instance with a different root directory
        return Dataset(new_root_dir)

    def with_image_format(self, name: str) -> "Dataset":
        """Adjust the file format of the output dataset, yielding new paths on the fly."""
        return Dataset(self.root_dir, output_format=name)

    def get_output_path_for_sample(self, sample: Sample) -> str:
        """Construct the output path based on the sample's relative path."""
        directory, filename = os.path.split(sample.relative_path)
        name, ext = os.path.splitext(filename)
        if self.output_format:
            ext = f".{self.output_format}"
        output_path = os.path.join(self.root_dir, directory, f"{name}{ext}")
        return output_path
