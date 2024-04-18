import argparse


def parse_args():
    parser = argparse.ArgumentParser(description="Transform & format image datasets")
    parser.add_argument("--src", type=str, help="The source path (input dataset's root directory).")
    parser.add_argument(
        "--dst", type=str, help="The destination path (output dataset's root directory)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="The destination path (output dataset's root directory)",
    )

    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    print("Your args:", args)
