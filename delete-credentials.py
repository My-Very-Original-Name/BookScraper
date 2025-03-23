import keyring
import json
from termcolor import colored
def get_credentials(site: str):
    """Retrieve stored credentials for a site."""
    try:
        usernames = keyring.get_credential(site, None) 
        if usernames:
            return usernames.username, keyring.get_password(site, usernames.username)
        return None, None
    except Exception:
        return None, None
def delete_credentials(site: str):
    """Delete stored credentials for a site."""
    username, _ = get_credentials(site)
    if username:
        keyring.delete_password(site, username)
        print(f"Deleted credentials for {site}")
    else:
        print(f"No credentials to delete for {site}")

def get_sites():
    with open("configs.json", "r") as f:
        config = json.load(f)
    return config["sites"]

def main():
    sites = get_sites()
    for i, site in enumerate(sites):
        print(f"{colored(i, "red")}: {colored(site, "yellow")}", end=" ")
    print()
    while 1:
        try:
            choice = int(input(colored("Enter site index: ", "light_blue")))
            if choice > len(sites) -1 or choice <0:
                raise ValueError
            break
            
        except ValueError:
            print(colored("Invalid input. Please enter a valid number.", "red"))
    delete_credentials(sites[choice])

if __name__ == "__main__":
    main()