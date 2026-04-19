import requests
import os
import shutil
import zipfile
import io
import sys

REPO = "My-Very-Original-Name/BookScraper"
VERSION_FILE = "version.txt"

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def check_updates():
    if "--post-update" in sys.argv:
        sys.argv.remove("--post-update")
        return

    try:
        clear_screen()
        print("Checking for updates...")
        res = requests.get(f"https://api.github.com/repos/{REPO}/commits/main")
        data = res.json()
        remote_sha = data["sha"][:7]
        if "sha" not in data:
            print(f"Could not check for updates: {data.get('message', 'unknown error')}")
            input("Press ENTER to continue...")
            return
        commit_message = data["commit"]["message"]
        
        local_sha = ""
        if os.path.exists(VERSION_FILE):
            with open(VERSION_FILE) as f:
                local_sha = f.read().strip()
            if local_sha == remote_sha:
                return  

        clear_screen()
        print(f"Current version: V{local_sha}")
        print(f"Update available: V{remote_sha}")
        print(f"Notes: {commit_message}")
        
        if input("\nUpdate now? (y/n): ").lower() != "y":
            return

        print("Downloading...")
        zip_res = requests.get(f"https://github.com/{REPO}/archive/refs/heads/main.zip")
        
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
        
        with open(VERSION_FILE, "w") as f:
            f.write(remote_sha)
        
        print("Update applied. Restarting...")
        try:
            os.execv(sys.executable, [sys.executable] + sys.argv + ["--post-update"])
        except OSError:
            print("Please relaunch the program manually.")
            exit(0)
        
    except Exception as e:
        print(f"Update failed: {e}")
        input("Press ENTER to continue with current version...")

if __name__ == "__main__":
    check_updates()
    import Scraper.core as core
    core.main()