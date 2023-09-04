import os

# creates the path to the root directory to be used in other modules
ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), ".."))

# local temporary folder
local_folder = os.path.join(ROOT_DIR, "temp_local")
