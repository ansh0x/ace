from pathlib import Path
import shutil
from .download_models import download_model
import json


def setup():

    HOME = Path.home() / ".ace"

    HOME.mkdir(parents=True, exist_ok=True)

    package_dir = Path(__file__).parent.resolve()
    config_file = ["applications.json", "hotkeys.json"]
    for filename in config_file:
        # Build absolute paths for source and destination
        src = package_dir / "config_files" / filename
        dst = HOME / filename

        # Copy the file (shutil.copy preserves permissions)
        if src.exists():
            shutil.copy(src, dst)
            print(f"Copied {filename} to {HOME}")
        else:
            print(f"Source file {filename} not found in {package_dir}")
    cache_size = int(input("Enter cache size to be used in KV-cache by LLM(in GB): \n"))

    config = {"version": "0.1.0", "home": str(HOME), "llm_cache_size": cache_size}

    Path(HOME / "cache" / "hotkey").mkdir(parents=True, exist_ok=True)

    with open(HOME / "config.json", "w") as f:
        json.dump(config, f)

    print("Downloading Models...")

    download_model(HOME / "models")
