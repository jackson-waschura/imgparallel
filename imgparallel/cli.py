"""
The Command Line Interface for imgparallel.

Example:
imgparallel --src test_data/input_images --dst /test_data/output_images --resize 512x512 --format jpg --proc 1
"""

import argparse
from typing import Dict, Any
from imgparallel.internal.dataset import Dataset
from imgparallel.internal.pipeline import Pipeline


def parse_args():
    parser = argparse.ArgumentParser(description="Transform & format image datasets")
    parser.add_argument("--src", type=str, help="The source path (input dataset's root directory).")
    parser.add_argument(
        "--dst", type=str, help="The destination path (output dataset's root directory)"
    )
    parser.add_argument(
        "--resize",
        type=str,
        default="same",
        help="Output image resolution, either 'same' or 'WxH'. Defaults to 'same'.",
    )
    parser.add_argument(
        "--format",
        type=str,
        default="same",
        help="Output image format, either 'same', 'png', or 'jpg'. 'jpeg' is interpreted as 'jpg'. Defaults to 'same'.",
    )
    parser.add_argument(
        "--proc",
        type=int,
        default=-1,
        help="Number of processes to use per stage. If set to -1, then this will be automatically determined.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Set up the pipeline but do not write any files.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Log extra information.",
    )

    return parser.parse_args()


def interpret_resize_args(arg: str) -> Dict[str, Any]:
    """
    Parses the resize argument into the format expected by the ResizeStage.
    """

    arg = arg.lower()

    if arg == "same":
        return {}
    
    dims = arg.split("x")

    if len(dims) < 2:
        raise ValueError("Invalid resize argument format. Expected format 'WxH'.")
    elif len(dims) > 2:
        raise ValueError("Invalid resize argument format. Too many dimensions specified.")
    
    width, height = dims
    width, height = int(width), int(height)
    
    return {"width": width, "height": height}


def interpret_format_args(arg: str) -> Dict[str, Any]:
    """
    Parses the format argument into the format expected by the Dataset.with_image_format method.
    """
    arg = arg.lower()

    if arg == "same":
        return {}

    return {"name": arg}


def main():
    args = parse_args()
    resize_kwargs = interpret_resize_args(args.resize)
    format_kwargs = interpret_format_args(args.format)
    input_dataset = Dataset(args.src)
    output_dataset = input_dataset.moved_to(args.dst).with_image_format(**format_kwargs)
    pipeline = Pipeline().read_images(input_dataset).resize(**resize_kwargs).write_images(output_dataset)
    pipeline.run(num_processes_per_stage=args.proc, verbose=args.verbose, dry_run=args.dry_run)
    print("Done!")


if __name__ == "__main__":
    main()