import os
import json
#local imports
from Scraper import ui

def get_configs(name:str):
    """
    name = web.name
    returns: output pdf path, cropping rectangle, sleep page (seconds), save credentials, bar
    """
    
    default_config = {
    "check-for-updates": True,
    "bar-length": 50,
    "save-credentials": True,
    "output-path": "output",
    "Zanichelli(Booktab)": {
        "resolution": [3840, 2160],
        "sleep-page-seconds": 1.5,
        "cropping-rectangle": [1189, 50, 2684, 2066]
    },
    "Hub-Scuola": {
        "resolution": [3840, 2160],
        "sleep-page-seconds": 1.5,
        "cropping-rectangle": [1212, 174, 2612, 1955]
    },
    "Loescher(Mylim)": {
        "resolution": [3840, 2160],
        "sleep-page-seconds": 0.5,
        "cropping-rectangle": [1098, 0, 2725, 2014]
    },
    "Sanoma": {
        "resolution": [3840, 2160],
        "sleep-page-seconds": 1.5,
        "cropping-rectangle": [1398, 26, 2894, 1977]
    },
    "Bsmart": {
        "resolution": [3840, 2160],
        "sleep-page-seconds": 2,
        "cropping-rectangle": [1131, 78, 2694, 2048]
    },
    "Cambridge": {
        "resolution": [3840, 2160],
        "sleep-page-seconds": 1.6,
        "cropping-rectangle": [1177, 96, 2651, 1954]
    },
    "Macmillan": {
        "resolution": [3840, 2160],
        "sleep-page-seconds": 0.5,
        "cropping-rectangle": [1177, 96, 2651, 1954]
    }
    } 
    if not os.path.exists("configs.json"):
        ui.print_warning("Missing configuration file, generating new one...", sleep_seconds=2)
        with open("configs.json", "w") as f:
            json.dump(default_config, f, indent = 4)

    with open("configs.json", "r") as file:
        f = json.load(file)

    check_for_added_conf_entries(f, default_config)

    try:
        with open("configs.json", "r") as file:
            f = json.load(file)

        return {
            "output_path": f["output-path"],
            "cropping_rectangle": f[name]["cropping-rectangle"],
            "sleep_page_seconds": f[name]["sleep-page-seconds"],
            "save_credentials": f["save-credentials"],
            "bar": ["░" for _ in range(f["bar-length"])],
            "resolution": f[name]["resolution"]
        }
    except Exception as e:
        ui.display_err_and_stop(None, f"Error loading configuration file: {e}")

def check_for_added_conf_entries(file, current_dict):
    missing_keys = current_dict.keys() - file.keys()
    if not missing_keys: 
        return False
    ui.print_warning("Missing entries in the configuration file, appending new ones...", sleep_seconds=2)
    
    
    for key in missing_keys:
        file[key] = current_dict[key]
    
    with open("configs.json", "w") as f:
        json.dump(file, f, indent = 4)
