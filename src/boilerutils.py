import os
import json

def get_home_dir():
    return os.path.expanduser("~")

TEST = True #TODO change

APP_NAME = "src-installer"

HOME_DIR = get_home_dir()
CWD = os.getcwd()
LOC_FILE = os.path.join(HOME_DIR, ".loc.json")
DEP_DIR = os.path.join(CWD, "dependencies")
CONF_DIR = os.path.join(CWD, "config")
if os.path.exists(LOC_FILE) and TEST is False:
    with open(LOC_FILE, "r") as f:
        loc = json.load(f)
        DEP_DIR = os.path.join(loc["dependencies"], APP_NAME)
        CONF_DIR = os.path.join(loc["config"], APP_NAME)
else:
    print("Using test values.")

FORMULA_DIR = os.path.join(DEP_DIR, "formula")
TARGET_DIR = os.path.join(DEP_DIR, "target")
TMP_DIR = os.path.join(DEP_DIR, "cache")
if os.path.exists(TMP_DIR) is False:
    os.mkdir(TMP_DIR)
BUILD_INSTRUCTION_DIR = os.path.join(DEP_DIR, "b_instructions")
PREFIX = os.path.join(CWD, "environment")