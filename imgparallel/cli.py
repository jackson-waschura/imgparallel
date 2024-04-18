"""
The Command Line Interface for imgparallel.

Example:
imgparallel --src /my_dataset/images --dst /my_new_dataset/images --resize 512x512 --format jpeg-90
"""

import argparse


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
        help="Output image format, either 'same', 'png', 'jpeg', or 'jpeg[-quality]'. 'jpg' is interpreted as 'jpeg'. Defaults to 'same'.",
    )
    parser.add_argument(
        "--proc",
        type=int,
        default=-1,
        help="Number of processes to use. If set to -1, then this will be automatically determined.",
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


if __name__ == "__main__":
    args = parse_args()
    print("Your args:", args)
