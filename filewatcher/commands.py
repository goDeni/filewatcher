import re

SIZE_POCKET = 10240

SHOW_FOLDER = "SHOW_FOLDER"


def is_show_folder(command: str) -> bool:
    return SHOW_FOLDER == command
