"""
Contains the utility methods used to read and write data.
"""

import cv2
import os
import tempfile
from numpy.typing import NDArray
from typing import Any

def read_image_from_path(img_path: str) -> NDArray[Any]:
    """
    Reads an image from the specified path and returns it as a numpy array.
    Raises FileNotFoundError if the image cannot be loaded.
    
    Parameters:
    img_path (str): Path to the image file.
    
    Returns:
    NDArray[Any]: Numpy array representing the loaded image.
    """
    img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
    if img is None:
        raise FileNotFoundError(f"Unable to load the image from the path: {img_path}")
    return img

def write_image_to_path(img_path: str, img_data: NDArray[Any]) -> None:
    """
    Writes an image to the specified path, inferring the format from the extension.
    Ensures that the directory exists and handles errors during the write process.

    Parameters:
    - img_path (str): The full path where the image should be saved, including filename.
    - img_data (NDArray[Any]): The image data to write.

    Raises:
    - FileNotFoundError: If the specified directory cannot be accessed or created.
    - IOError: If the image write operation fails.
    """
    
    # Ensure the directory exists
    directory = os.path.dirname(img_path)
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

    # Attempt to write the image to the specified path
    result = cv2.imwrite(img_path, img_data)
    if not result:
        # Handle failed write operation
        raise IOError(f"Failed to write the image to '{img_path}'. Check the image data and file path.")

def check_permissions(test_path):
    try:
        # Try creating a temporary directory
        temp_dir = os.path.join(test_path, tempfile.mkdtemp())
        # Try creating a temporary file
        temp_file = tempfile.mkstemp(dir=test_path)
        os.close(temp_file[0])  # Close the file descriptor
        return True
    except PermissionError:
        return False
    finally:
        # Clean up
        if 'temp_file' in locals():
            os.unlink(temp_file[1])  # Remove the file created
        if 'temp_dir' in locals():
            os.rmdir(temp_dir)  # Remove the temporary directory