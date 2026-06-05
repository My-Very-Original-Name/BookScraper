import requests
import os
import shutil
import zipfile
import io
import sys
import json
import time

REPO = "My-Very-Original-Name/BookScraper"
VERSION_FILE = "version.txt"
VERSION_FILE = os.path.join("Scraper", "version.txt")
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def check_updates():
    if "--post-update" in sys.argv:
        sys.argv.remove("--post-update")
        return
    if os.path.exists("configs.json"):
        try:
            with open("configs.json", "r") as f:
                data = json.load(f)
            if data["check-for-updates"] == False:
                return
        except Exception:
            print("ERROR: Missing configuration 'check-for-updates' in 'config.json', aborting update_check...")
            time.sleep(4)
            return
    try:
        clear_screen()
        print("Checking for updates...")
        res = requests.get(f"https://api.github.com/repos/{REPO}/releases/latest")
        data = res.json()

        if "tag_name" not in data:
            print("No releases found or API error.")
            return
        
        remote_version = data["tag_name"]
        release_notes = data["body"]
        current_version = "Version unavailable"
        if os.path.exists(VERSION_FILE):
            with open(VERSION_FILE, "r") as f:
                current_version = f.read()
        if current_version == remote_version:
            return

        clear_screen()
        print(f"Current version: {current_version}")
        print(f"Update available: {remote_version}")
        print(f"Notes: {release_notes}")
        
        if input("\nUpdate now? (y/N): ").lower() != "y":
            return

        print("Downloading...")
        zip_url = data["zipball_url"]
        zip_res = requests.get(zip_url)
        
        with zipfile.ZipFile(io.BytesIO(zip_res.content)) as z:
            if os.path.exists("Scraper"):
                shutil.rmtree("Scraper")
            
            for file in z.namelist():
                if "Scraper/" in file:
                    parts = file.split("/")
                    idx = parts.index("Scraper")
                    target_path = os.path.join(*parts[idx:])
                    if not os.path.abspath(target_path).startswith(os.path.abspath("Scraper")):
                        continue
                    if file.endswith("/"):
                        os.makedirs(target_path, exist_ok=True)
                    else:
                        with z.open(file) as src, open(target_path, "wb") as dst:
                            shutil.copyfileobj(src, dst)
        
        print("Update applied. Restarting...")
        try:
            os.execv(sys.executable, [sys.executable] + sys.argv + ["--post-update"])
        except OSError:
            print("Please relaunch the program manually.")
            exit(0)
        
    except Exception as e:
        print(f"An unexpected error occured, Update failed: {e}")
        input("Press ENTER to exit")
        exit(1)

if __name__ == "__main__":
    check_updates()
    import Scraper.core as core
    core.main()