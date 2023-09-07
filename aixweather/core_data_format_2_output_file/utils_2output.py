import os

from config.definitions import ROOT_DIR


def result_folder_path() -> str:
    folder_path = os.path.join(f"{ROOT_DIR}", "results")
    return folder_path

def results_file_path(filename: str, folder_path: str = None) -> str:
    """
    create a path to a results file

    Args:
        filename: name of file
        folder_path: path to result folder

    Returns:
        str: path to result file
    """
    # if required specify folder_path e.g. for Django WebApp
    if folder_path is None:
        folder_path = result_folder_path()

    # Ensure that the results folder exists
    os.makedirs(folder_path, exist_ok=True)

    # create file path
    filepath = os.path.join(folder_path, filename)
    return filepath
