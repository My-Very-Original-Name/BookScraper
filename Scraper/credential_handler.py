import keyring
import getpass
import json
import keyring.errors
#local imports
from . import ui
import logging
logging.getLogger("dbus.proxies").setLevel(logging.CRITICAL)
ACCOUNT = "bookscraper"

class Credentials():
    def save_credentials(self, site: str, username: str, password: str):
        try:
            keyring.set_password(site, ACCOUNT, json.dumps({"username": username, "password": password}))
        except Exception as e:
            ui.print_warning(f"Could not save credentials to the system keyring: {e}", sleep_seconds=2)

    def get_credentials(self, site: str):
        try:
            raw = keyring.get_password(site, ACCOUNT)
            if raw:
                data = json.loads(raw)
                return data["username"], data["password"]

            # Legacy fallback
            legacy = keyring.get_credential(site, None)
            if legacy and legacy.username:
                password = keyring.get_password(site, legacy.username)
                if password:
                    self.save_credentials(site, legacy.username, password)  # migrate
                    self._delete_legacy_credentials(site)
                    return legacy.username, password
        except Exception:
            pass
        return None, None

    def _delete_legacy_credentials(self, site:str):
        try:  #clear legacy entry
            legacy = keyring.get_credential(site, None)
            if legacy and legacy.username:
                keyring.delete_password(site, legacy.username)
                deleted = True
        except Exception:
            pass

    def delete_credentials(self, site: str):
        deleted = False
        try:
            keyring.delete_password(site, ACCOUNT)
            deleted = True
        except keyring.errors.KeyringError:
            pass
        self._delete_legacy_credentials(site)
        print(f"Deleted credentials for {site}" if deleted else f"No credentials to delete for {site}")
        

def get_credentials(web_name:str, save_credentials: bool, correct_old_credentials = False):
    deleted = False
    credentials = Credentials()

    if correct_old_credentials and not save_credentials: 
        credentials.delete_credentials(web_name)
        deleted = True

    username, password = credentials.get_credentials(web_name)

    if save_credentials and username and not correct_old_credentials:
        username, password = credentials.get_credentials(web_name)
        
        if ui.generic_user_prompt("[/#00E5FF]Using saved credentials: [purple]if you want to delete them enter: \"d\"[/purple]\nIf you want to disable credential saving, set \"save-credentials\" in \"configs.json\" to false. \nOtherwise, [purple]Press ENTER to continue[/purple][#00E5FF]", choices=["d", ""], show_choices= False, default_choice="") == "d":
            credentials.delete_credentials(web_name)
            ui.clear_console()
            print(ui.color("Credentials deleted successfully.\n", "green"))
            deleted = True

    if save_credentials and (not username or deleted):
        ui.print_reminder("Credential saving is set to True. The following credentials will be stored safely.\nIf you want to disable this behavior, set \"save-credentials\" in \"configs.json\" to false.")
    
    if not username or not save_credentials or deleted:
        while True:
            username = getpass.getpass(ui.color(f"Enter your {web_name} username: ","blue"))
            password = getpass.getpass(ui.color(f"Enter your {web_name} password: ","blue"))
            if username and password: break
            ui.clear_console()
            print(ui.color("Invalid credentials. Please try again.", "red"))
        ui.clear_console()
        if save_credentials:
            credentials.save_credentials(web_name ,username, password)
    return username, password
