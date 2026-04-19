# BookScraper
Bookscraper is a python-built tool that converts **owned e-books** from Italian educational sites into PDFs for local personal use to bypass the clunky and slow proprietary e-readers provided by publishers.

## Key features

- **Interactive page cropping:** Built-in GUI to visually select the page area to exclude UI elements.
- **Secure credential handling:** Integrates with your system's native keyring (see usage section).
- **Auto updates:** Stays in sync with the latest scraper logic from the repository.

## Supported platforms:

- **Zanichelli** (Booktab)

> [!WARNING]
>
> Zanichelli does not work in headless mode, when scanning it will open a browser window. Do not resize or close it.

- **Hub scuola**

- **Loescher** (Mylim)

- **Sanoma**

- **Bsmart**

- **Cambridge**

> [!WARNING]
>
> Due to how Cambridge formats the e-books, not all of them are scannable. If your book is presented as a hybrid where multiple pages are stitched together and scrollable it is most likely not supported.

## Installation
### Prerequisites

- **Python 3.12+**
- **Firefox browser**

> [!WARNING]
>
> **Fellow Linux users:** Tkinter is required but its not always bundled with python for some reason. Ensure you have it installed: `sudo apt-get install python3-tk`

### Setup

1. Clone the repo:

   ```bash
   git clone https://github.com/My-Very-Original-Name/BookScraper.git
   ```

2.  install python libraries:

    ```bash
    pip install -r requirements.txt
    ```


> [!NOTE]
>
> Selenium should manage the driver automatically, but if the program is crashing make sure that `geckodriver` is installed on your system path.

## Usage

Run `run.py` from the root directory:

  ```bash
  python run.py
  ```

### Updating

On startup the program will automatically look for updates. If found it will reinstall the `Scraper/` directory. It will **not** overwrite configurations or delete the output folder. This  can be disabled in `configs.json`

### Credential Handling

BookScraper needs the user's credentials to log into the sites that host the e-books. The program will ask for credentials directly in the console, there is no need to save them anywhere in the configuration files. By default said credentials will be saved in the system's credential manager/wallet for automatic access in following runs. This behavior can be disabled in `configs.json`

## Configuration

All the configurable settings are found in `configs.json` inside the main directory.

### General settings

```json
"output-path": "output",
"save-credentials": true,
"check-for-updates": true,
```

**output-path:** specify the output directory.

**save-credentials:** toggles credential saving in the system's credential manager. 

> [!Warning]
>
> Disabling credential saving while having already stored credentials will not delete them. To delete them you must keep it on and delete them in the program when prompted.

**check for updates:** toggles update check at startup

### Site specific settings

```json
"Zanichelli(Booktab)": {
    "resolution": [
        3840,
        2160
    ],
    "sleep-page-seconds": 1.5,
    "cropping-rectangle": [
        1189,
        50,
        2684,
        2066
    ]
},
```

**resolution:** [x,y] Sets the resolution at which the headless browser window is rendered.

> [!NOTE]
>
> The final image resolution seen in the output pdf will not be the same as the **resolution** setting as the image will be cropped to remove all of the site's UI

**sleep-page-seconds:** Sets the amount of time the scraper will wait for each page to load.

> [!TIP]
>
> Most sites are quite unreliable when it comes to loading speed, I have found Hub-scuola to be the worst one. Adjust this setting to suit your specific network speed

**cropping-rectangle:** [left, up, right, bottom] Sets the default crop area (in pixel coordinates) for the specific site, it functions as a fall-back if the  user does not specify a precise one when prompted. 

## Notice

I am a solo student and generally update the scraping logic only whenever i actually need to use it. If anyone actually ends up downloading this and a site update breaks the tool feel free to open an issue and ill' try to help out.

## DISCLAIMER

This program is intended **strictly for personal use** with books you legally **own**. I do not in any way condone the distribution of unlicensed content or the bypassing of DRM for copyright infringement.

**Use at your own risk:** I am not responsible for any account suspensions or legal issues resulting from the use of this software

