import json
import os
from . import config


def _flatten_hotkeys(hotkey_db=None):
    """
    Convert nested structure to flat dictionary

    Input:
    {
      "general": {
        "close_window": {
          "key": "mod+w",
          "desctiption": "Close current focused window"
        }
      }
    }

    Output:
    {
      "general-close_window": {
        "key": "mod+w",
        "description": "Close current focused window",
        "category": "general",
        "action": "close_window"
      }
    }
    """

    if hotkey_db is None:
        with open(
            os.path.join(config.HOME, "cache", "hotkey", "hotkey_db.json"), "r"
        ) as f:
            hotkey_db = json.load(f)

    flattened = {}

    for category, actions in hotkey_db.items():
        for action_name, action_data in actions.items():
            # Build full hotkey name: "general-close_window"
            full_name = f"{category}-{action_name}"

            description = action_data.get("description")

            flattened[full_name] = {
                "key": action_data.get("key", ""),
                "description": description,
                "category": category,
                "action": action_name,
            }

    return flattened


def _read_file(file_path: str) -> dict[str, str] | list[str]:
    """
    Reads the file at the give `file_path` and returns.
    Currently only supports .txt and .json files.
    """
    if not os.path.exists(file_path):
        print(f"File path: {file_path} do not exist.")
        return False
    ext = file_path.split(".")[-1]
    if ext == "json":
        with open(file_path, "r") as f:
            return json.load(f)

    if ext == "txt":
        with open(file_path, "r") as f:
            data = []
            for line in f:
                data.append(line.strip())

            return data
