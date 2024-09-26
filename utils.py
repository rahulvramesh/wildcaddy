import os
import sys

def get_data_dir():
    """
    Get the path to the Wild Caddy data directory in the user's Application Support folder.
    Create the directory if it doesn't exist.
    """
    # Get the Application Support directory
    app_support_dir = os.path.join(
        os.path.expanduser("~"), "Library", "Application Support"
    )

    # Create a directory specifically for Wild Caddy
    data_dir = os.path.join(app_support_dir, "Wild Caddy")

    try:
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
    except OSError as e:
        raise OSError(f"Failed to create directory '{data_dir}': {str(e)}")

    return data_dir
