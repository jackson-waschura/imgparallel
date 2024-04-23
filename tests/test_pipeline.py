import pytest
import os
import tempfile
import random
import cv2
import numpy as np
import shutil

from imgparallel.internal.dataset import Dataset
from imgparallel.internal.pipeline import Pipeline


# Fixture setup
@pytest.fixture
def temp_dirs():
    input_dir = tempfile.mkdtemp()
    output_dir = tempfile.mkdtemp()
    temp_file = tempfile.mktemp()
    yield input_dir, output_dir, temp_file
    # Cleanup after test
    shutil.rmtree(input_dir)
    shutil.rmtree(output_dir)


def generate_random_image(width, height):
    """Generate a random image of specified size using OpenCV."""
    # Generate a random array and convert it to a uint8 image
    image = np.random.randint(0, 256, (height, width, 3), dtype=np.uint8)
    return image


def test_full_pipeline(temp_dirs):
    input_dir, output_dir, temp_file = temp_dirs

    N = 10  # Number of images
    HEIGHT_OUT = 256
    WIDTH_OUT = 320

    sizes = [(random.randint(100, 1000), random.randint(100, 1000)) for _ in range(N)]
    subdirs = ["subdir1", "subdir2"]

    # Ensure subdirectories are created
    for subdir in subdirs:
        os.makedirs(os.path.join(input_dir, subdir))

    # Generate and save images
    expected_imgs = {}
    for i in range(N):
        img = generate_random_image(*sizes[i])
        if i % 2 == 0:  # Save some images in subdirectories
            subdir = random.choice(subdirs)
            path = os.path.join(input_dir, subdir, f"image_{i}.png")
        else:
            path = os.path.join(input_dir, f"image_{i}.png")

        # Write the original with OpenCV
        cv2.imwrite(path, img)

        # Calculate the expected output, including jpg compression
        rel_path = os.path.relpath(path, input_dir)
        img = cv2.resize(img, (WIDTH_OUT, HEIGHT_OUT))
        cv2.imwrite(temp_file + ".jpg", img)
        expected_imgs[rel_path] = cv2.imread(temp_file + ".jpg", cv2.IMREAD_UNCHANGED)

    # Run the actual pipeline
    input_dataset = Dataset(input_dir)
    output_dataset = input_dataset.moved_to(output_dir).with_image_format(name="jpg")
    pipeline = (
        Pipeline()
        .read_images(input_dataset)
        .resize(width=WIDTH_OUT, height=HEIGHT_OUT)
        .write_images(output_dataset)
    )
    pipeline.run(num_processes_per_stage=1)

    # Compare to the expected output
    for rel_path, expected_img in expected_imgs.items():
        # Adjust the file path for the output directory and change extension to .jpg
        output_path = os.path.join(output_dir, os.path.splitext(rel_path)[0] + ".jpg")
        processed_img = cv2.imread(output_path, cv2.IMREAD_UNCHANGED)

        # Ensure the file exists
        assert processed_img is not None, f"Expected output file {output_path} does not exist."

        # Check the image size
        assert (
            processed_img.shape == expected_img.shape
        ), f"Image size mismatch for {output_path}: expected {expected_img.shape}, got {processed_img.shape}"

        # Check if the image content matches
        np.testing.assert_allclose(
            processed_img, expected_img
        ), f"Image data mismatch for {output_path}. Images are not identical."
