import glob, os, pathlib


def get_file_path(download_path):
    """Return the path of the most recently downloaded file."""
    list_of_files = glob.glob(download_path + "/*")
    latest_file = max(list_of_files, key=os.path.getctime)
    return pathlib.Path(latest_file)
