import os

from config.definitions import ROOT_DIR

def results_file_path(filename:str, folder_path:str=None):
    """
    create a path to file
        Parameter:
            filename: (string)
        Return
            file path
    """
    # if required specify folder_path e.g. for Django WebApp
    if folder_path is None:
        filepath = os.path.join(f"{ROOT_DIR}", "results", filename)
    else:
        filepath = os.path.join(folder_path, filename)
    return filepath
