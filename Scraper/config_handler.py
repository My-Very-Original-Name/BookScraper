import os
import json
#local imports
from .utils import color, stop

def get_configs(name:str):
    """
    name = web.name
    returns: output pdf path, cropping rectangle, sleep page (seconds), save credentials, bar
    """
    if not os.path.exists("configs.json"):
        default_config = {"output-path": "output",
    "bar-length": 50,
    "save-credentials": True,
    "output-path": "output",
    "sites": [
        "Zanichelli(Booktab)",
        "Hub-Scuola",
        "Loescher(Mylim)",
        "Sanoma",
        "Bsmart",
        "Cambridge"
    ],
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
    }} 
        print(f"{color("WARNING: ", "yellow")}: Missing configuration file, generating new one...")
        with open("configs.json", "w") as f:
            json.dump(default_config, f, indent = 4)
    try:
        with open("configs.json", "r") as file:
            f = json.load(file)
        return {
            "output_path": f["output-path"],
            "cropping_rectangle": f[name]["cropping-rectangle"],
            "sleep_page_seconds": f[name]["sleep-page-seconds"],
            "save_credentials": f["save-credentials"],
            "bar": ["░" for _ in range(f["bar-length"])],
            "sites_list": f["sites"],
            "resolution": f[name]["resolution"]
        }
    except Exception as e:
        stop(1, f"Error loading configuration file: {e}")

def load_site_list():
    if not os.path.exists("configs.json"):
        return [
        "Zanichelli(Booktab)",
        "Hub-Scuola",
        "Loescher(Mylim)",
        "Sanoma",
        "Bsmart",
        "Cambridge"
        ]
    with open("configs.json", "r") as f:
        return json.load(f)["sites"]