import keyring
import getpass
#local imports
from . import utils
class Credentials():
    def save_credentials(self,site: str, username: str, password: str):
        keyring.set_password(site, username, password)

    def get_credentials(self,site: str):
        try:
            usernames = keyring.get_credential(site, None)  
            if usernames:
                return usernames.username, keyring.get_password(site, usernames.username)
            else:
                return None, None 
        except Exception as e:
            return None, None
    def delete_credentials(self, site: str):
        username, _ = self.get_credentials(site)
        if username:
            keyring.delete_password(site, username)
            print(f"Deleted credentials for {site}")
        else:
            print(f"No credentials to delete for {site}")

def get_credentials(web_name:str, save_credentials: bool):
    utils.clear_console()
    credentials = Credentials()
    username, password = credentials.get_credentials(web_name)
    deleted = False
    if  save_credentials and username:
        username, password = credentials.get_credentials(web_name)
        if input(utils.color("NOTICE:  ", "yellow")+ "using saved credentials: "+utils.color("if you want to delete them enter: \"d\"", "purple")+"\nIf you want to disable credential saving, set \"save-credentials\" in \"configs.json\" to false. \nOtherwise: "+ utils.color("Press ENTER to continue ", "purple")).lower() == "d":
            credentials.delete_credentials(web_name)
            utils.clear_console()
            print(utils.color("Credentials deleted successfully.\n", "green"))
            deleted = True
    if save_credentials and (not username or deleted):
        print(f"{utils.color("NOTICE:", "yellow")} credential saving is set to True. the following credentials will be stored safely,\nIf you want to disable this behavior, set \"save-credentials\" in \"configs.json\" to false.")
    if not username or not save_credentials or deleted:
        while True:
            username = getpass.getpass(utils.color(f"Enter your {web_name} username: ","blue"))
            password = getpass.getpass(utils.color(f"Enter your {web_name} password: ","blue"))
            if username and password: break
            utils.clear_console()
            print(utils.color("Invalid credentials. Please try again.", "red"))
        utils.clear_console()
        if save_credentials:
            credentials.save_credentials(web_name ,username, password)
    return username, password
