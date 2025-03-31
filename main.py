from PIL import Image
import img2pdf
import io
import time
from PyPDF2 import PdfMerger
import os
import shutil
from termcolor import colored
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.firefox.options import Options
from tabulate import tabulate
from random import randint
import msvcrt
import sys
import json
import keyring


# ---- Classes ----
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

class _Base_web():
    def take_screenshot(self):
        return self.driver.get_screenshot_as_png()

    def quit(self):
        self.driver.quit()
    def _setup_driver(self, url, resolution):
        options = Options()
        options.headless = True
        self.driver = webdriver.Firefox(options=options)
        self.driver.set_window_size(resolution[0], resolution[1])
        self.driver.get(url)
        self.wait = WebDriverWait(self.driver, 10)
    
class Zanichelli(_Base_web):

    def __init__(self):
        self.name = "Zanichelli(Booktab)"

    def start(self, username, password, resolution):
        self._setup_driver("https://my.zanichelli.it/", resolution)
        self._enter_credentials(username, password)
        self._accept_cookies()
        self._select_book()

    def _enter_credentials(self, username, password):
        email_input = self.wait.until(EC.presence_of_element_located((By.ID, "inline-username-input")))
        password_input = self.driver.find_element(By.ID, "inline-password-input")

        email_input.send_keys(username)
        password_input.send_keys(password)

        self.driver.find_element(By.CLASS_NAME, "z-button--container").click()
        self.wait.until(EC.presence_of_element_located((By.ID, "home")))

    def _accept_cookies(self):
        try:
            self.wait.until(EC.presence_of_element_located((By.ID, "onetrust-accept-btn-handler"))).click()
        except Exception:
            pass 

    def _select_book(self):
        buttons = self.driver.find_elements(By.CSS_SELECTOR, "button[aria-label*='LEGGI EBOOK']")
        books = [[colored(str(i), "red"), btn.get_attribute("aria-label").split("LEGGI EBOOK")[-1].strip()] for i, btn in enumerate(buttons)]

        clear_console()
        print(f"{colored("WARNING: ", "red")}books must already be set to double page mode and to the firts page")
        print(tabulate(books, headers=['Index', 'Name'], tablefmt='pipe', colalign=("center", "center")))
        i = get_numeric_input("\nInsert book index: ", 0, len(buttons) - 1)
        self.book = buttons[i].get_attribute("aria-label").split("LEGGI EBOOK")[-1].strip()
        buttons[i].click()
        self.driver.switch_to.window(self.driver.window_handles[1])
        time.sleep(5)  
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "button[aria-label='Vista pagina singola (Ctrl + Shift + V)']"))).click()

    def turn_page(self):
        self.wait.until(EC.presence_of_element_located((By.ID, "default_next_bttn"))).click()

    
class Hub_scuola(_Base_web):
    def __init__(self):
        self.name = "Hub-Scuola"


    def start(self, username, password, resolution):
        self._setup_driver("https://www.hubscuola.it/login", resolution)
        self._accept_cookies()
        self._enter_credentials(username, password)
        clear_console()
        self._select_book()
        clear_console()
        self._select_edition()
    def _enter_credentials(self, username, password):
        self.wait.until(EC.presence_of_element_located((By.ID, ":r6:"))).send_keys(username)
        self.driver.find_element(By.ID, ":r7:").send_keys(password)
        self.driver.find_elements(By.XPATH, "//button//span[text()='Accedi']")[1].click()
        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME,"R7FWxhKTRu2I206FyL0A")))
    def _select_book(self):
        time.sleep(2)
        elements = self.driver.find_elements(By.CLASS_NAME, "zW9ivNHXZ2LXEAF2iGDo")
        buttons = self.driver.find_elements(By.XPATH, "//button//span[text()='Esplora']")
        books = [[colored(str(elements.index(element)), "red"), element.text[:50]]for element in elements]
        print(tabulate(books, headers=['Index', 'Name'], tablefmt='pipe', colalign=("center", "center")))
        i = get_numeric_input("\nInsert book index: ", 0, len(elements) - 1)
        self.book = elements[i].text
        buttons[i].click()
        
    
    def _select_edition(self):
        time.sleep(2)
        all_links = self.driver.find_elements(By.TAG_NAME, "a")
        first_type_links = []
        for link in all_links:
            href = link.get_attribute("href")
            if href and "young.hubscuola.it" in href:
                svg_elements = link.find_elements(By.TAG_NAME, "svg")
                if svg_elements:  
                    first_type_links.append(link)
        books = [[colored(str(first_type_links.index(element)), "red"), element.text[:50]]for element in first_type_links]
        print(tabulate(books, headers=['Index', 'Name'], tablefmt='pipe', colalign=("center", "center")))
        i = get_numeric_input("\nInsert book index: ", 0, len(first_type_links) - 1)
        first_type_links[i].click()
        self.driver.switch_to.window(self.driver.window_handles[1])
        time.sleep(5)
    def _accept_cookies(self):
        time.sleep(2)
        try:
            self.wait.until(EC.presence_of_element_located((By.XPATH, "//button[contains(@class, 'iubenda-cs-accept-btn') and text()='Accetta e chiudi']"))).click()
        except Exception:
            pass  
    def turn_page(self):
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.g-btn-page.g-btn-page--next"))).click()

class Mylim(_Base_web):
    def __init__(self):
        self.name = "Loescher(Mylim)"
    def start(self, username, password, resolution):
        self._setup_driver("https://mylim.loescher.it/#!/login", resolution)
        self._enter_credentials(username, password)
        self._select_book()
    def _enter_credentials(self, username, password):
        self.wait.until(EC.presence_of_element_located((By.XPATH, "//button[contains(@class, 'mantine-Button-root') and .//span[text()='Accetta']]"))).click()
        self.wait.until(EC.presence_of_element_located((By.ID, "mantine-r1"))).send_keys(username)
        self.wait.until(EC.presence_of_element_located((By.ID, "mantine-r2"))).send_keys(password)
        self.driver.find_element(By.XPATH, "//button[contains(@class, 'mantine-Button-root') and .//span[text()='Entra']]").click()
    def _select_book(self):
        time.sleep(2)
        elements = self.wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "PdfCard-module__titolo___UX1Y_")))
        books = [[colored(str(i), "red"), element.text] for i, element in enumerate(elements)]

        clear_console()
        print(tabulate(books, headers=['Index', 'Name'], tablefmt='pipe', colalign=("center", "center")))
        i = get_numeric_input("\nInsert book index: ", 0, len(elements) - 1)
        self.book = elements[i].text
        elements[i].click()
        self.wait.until(EC.presence_of_element_located((By.NAME, "next-page")))
        clear_console()
        print("Waiting for book to load...")
        time.sleep(15)
        
        
    def turn_page(self):
        self.wait.until(EC.presence_of_element_located((By.NAME, "next-page"))).click()

class Sanoma(_Base_web):
    def __init__(self):
        self.name = "Sanoma"
    def start(self, username, password, resolution):
        self._setup_driver("https://place.sanoma.it/", resolution)
        self._enter_credentials(username, password)
        self._select_book()
    def _enter_credentials(self, username, password):
        self.wait.until(EC.presence_of_element_located((By.NAME, "text"))).send_keys(username)
        time.sleep(0.5)
        self._accept_cookies()
        self.driver.find_element(By.XPATH, "//button[@title='Accedi']").click()
        time.sleep(2)
        self.wait.until(EC.presence_of_element_located((By.NAME, "password"))).send_keys(password)
        self.driver.find_element(By.NAME, "submit").click()
    def _accept_cookies(self):
        try:
            self.driver.find_element(By.ID, "ppms_cm_agree-to-all").click()
            self.wait.until(EC.presence_of_element_located((By.ID, "ppms_consent_form_success_note_button"))).click()
        except Exception:
            pass
    def _select_book(self):
        self.wait.until(EC.presence_of_element_located((By.XPATH, "//a[@href='/prodotti_digitali']"))).click()
        elements = self.wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "title")))
        books = [[colored(str(i), "red"), element.text] for i, element in enumerate(elements)]
        clear_console()
        print(tabulate(books, headers=['Index', 'Name'], tablefmt='pipe', colalign=("center", "center")))
        self.driver.find_elements(By.CLASS_NAME, "button-open")[get_numeric_input("\nInsert book index: ", 0, len(elements) - 1)].click()
        editions = self.driver.find_elements(By.CLASS_NAME, "volume")
        clear_console()
        books = [[colored(str(i), "red"), element.text] for i, element in enumerate(editions)]
        print(tabulate(books, headers=['Index', 'Name'], tablefmt='pipe', colalign=("center", "center")))
        editions[get_numeric_input("\nInsert book index: ", 0, len(editions) - 1)].click()
        sub_editions = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@href, 'prodotti_digitali/libromedia')]")))
        clear_console()
        books = [[colored(str(i), "red"), element.text] for i, element in enumerate(sub_editions)]
        print(tabulate(books, headers=['Index', 'Name'], tablefmt='pipe', colalign=("center", "center")))
        i = get_numeric_input("\nInsert book index: ", 0, len(sub_editions) - 1)
        self.book = sub_editions[i].text
        sub_editions[i].click()
        self.driver.switch_to.window(self.driver.window_handles[1])
        clear_console()
        print("Waiting for book to load...")
        time.sleep(7)
        self.wait.until(EC.frame_to_be_available_and_switch_to_it((By.TAG_NAME, "iframe")))
        self.driver.find_element(By.CSS_SELECTOR, "span.icon.icon-page-single").click()
        self.driver.find_element(By.ID, "page-field").send_keys("1")
        self.driver.find_element(By.ID, "page-field").send_keys(Keys.ENTER)
    def turn_page(self):
        self.wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(@class, 'turn-page right')]"))).click()

class Bsmart(_Base_web):
    def __init__(self):
        self.name = "Bsmart"
    def start(self, username, password, resolution):
        self._setup_driver("https://www.bsmart.it/users/sign_in", resolution)
        self._enter_credentials(username, password)
        self._select_book()
    def _enter_credentials(self, username, password):
        self.wait.until(EC.presence_of_element_located((By.ID, "user_email"))).send_keys(username) 
        self.driver.find_element(By.ID, "user_password").send_keys(password)
        self.driver.find_element(By.NAME, "commit").click()
    def _accept_cookies(self):
        try:
            time.sleep(2)
            self.driver.find_element(By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll").click()
        except Exception as e:
            pass
    def _select_book(self):
        self.wait.until(EC.presence_of_element_located((By.LINK_TEXT, "BSMART BOOKS (new)"))).click()
        self.driver.switch_to.window(self.driver.window_handles[1])
        self.wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/books/')]")))
        self._accept_cookies()
        elements = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/books/'][data-discover='true']")
        titles = []
        elements_text = []
        for element in elements:
            if element.text:
                titles.append(element.text)
            elements_text.append(element.text)
        books = [[colored(str(i), "red"), title] for i, title in enumerate(titles)]
        clear_console()
        print(tabulate(books, headers=['Index', 'Name'], tablefmt='pipe', colalign=("center", "center")))
        i = get_numeric_input("\nInsert book index: ", 0, len(elements) - 1)
        i = elements_text.index(titles[i])
        self.book = elements[i].text
        elements[i].click()
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "button[title='Vai alla pagina successiva']")))
        self.driver.find_elements(By.CSS_SELECTOR, "button[aria-pressed='false'].inline-flex.items-center.justify-center.h-fit")[4].click()
        self.driver.find_element(By.XPATH, "//li[contains(@class, 'dark:text-white') and contains(., 'Disposizione pagine')]").find_element(By.XPATH, ".//button[contains(@class, 'inline-flex')]").click()
        button = self.driver.find_elements(By.XPATH, "//button[contains(@class, 'inline-flex')]")[6]
        self.driver.execute_script("arguments[0].click();", button)
    def turn_page(self):
        self.driver.find_element(By.CSS_SELECTOR, "button[title='Vai alla pagina successiva'].flex.justify-center.items-center.absolute").click()
class Cambridge(_Base_web):
    def __init__(self):
        self.name = "Cambridge"
    def start(self, username, password, resolution):
        self._setup_driver("https://www.cambridge.org/go/login", resolution)
        self._enter_credentials(username, password)
        self._select_book()
    def _enter_credentials(self, username, password):
        self._accept_cookies()
        time.sleep(1.5)
        self.wait.until(EC.presence_of_element_located((By.ID, "gigya-loginID-75570100315269100"))).send_keys(username)
        self.driver.find_elements(By.CLASS_NAME, "gigya-input-submit")[6].click()
        self.wait.until(EC.presence_of_element_located((By.ID, "gigya-password-28556111034728640"))).send_keys(password)
        self.driver.find_elements(By.CLASS_NAME, "gigya-input-submit")[6].click()
        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "card-title")))
    def _select_book(self):
        clear_console()
        print(f"{colored("WARNING: ", "red")} Not all Cambridge-Go books are supported, check on the reader manually, if it's formatted as a scrolling book (one page below the other) it will not be scannable.\n{colored("WARNING: ", "red")} Supported books must be already set to DOUBLE PAGE MODE")
        elements = self.driver.find_elements(By.CLASS_NAME, "card-details")
        books = [[colored(str(elements.index(element)), "red"), element.text]for element in elements]
        print(tabulate(books, headers=['Index', 'Name'], tablefmt='pipe', colalign=("center", "center")))
        i = get_numeric_input("\nInsert book index: ", 0, len(books)-1)
        self.book = elements[i].text
        elements[i].click()
        elements = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='section-grid']//*[contains(@class, 'font-weight-bold') and contains(@class, 'card-title') and contains(@class, 'text-body-1')]")))
        books = [[colored(str(elements.index(element)), "red"), element.text]for element in elements]
        clear_console()
        print(tabulate(books, headers=['Index', 'Name'], tablefmt='pipe', colalign=("center", "center")))
        i = get_numeric_input("\nInsert book index: ", 0, len(books)-1)
        self.book = self.book + elements[i].text
        elements[i].click()
        time.sleep(1.5)
        self.driver.switch_to.window(self.driver.window_handles[1])
        print("Waiting for book to load...")
        time.sleep(10)
        clear_console()
        try:
            self.wait.until(EC.frame_to_be_available_and_switch_to_it((By.TAG_NAME, "iframe")))
            self.wait.until(EC.presence_of_element_located((By.ID, "zoom-singlePage"))).click()
        except Exception:
            stop(1, "Not able to find test element, book may not be supported.")
        
    def turn_page(self):
        self.driver.find_element(By.ID, "next-page-button").click()
            
    def _accept_cookies(self):
        try:
            self.wait.until(EC.presence_of_element_located((By.ID, "onetrust-accept-btn-handler"))).click()
        except Exception:
            pass



# ---- Global variables ----
classes = [Zanichelli(), Hub_scuola(), Mylim(), Sanoma(), Bsmart(), Cambridge(),]
pdf_merger = PdfMerger()
credentials = Credentials()

# ---- Helper functions -------------------------------
def clear_console():
    os.system("cls" if os.name == "nt" else "clear")
    sys.stdout.flush()
    print(colored(r"""    ____                 __   _____                                      
   / __ ) ____   ____   / /__/ ___/ _____ _____ ____ _ ____   ___   _____
  / __  |/ __ \ / __ \ / //_/\__ \ / ___// ___// __ `// __ \ / _ \ / ___/
 / /_/ // /_/ // /_/ // ,<  ___/ // /__ / /   / /_/ // /_/ //  __// /    
/_____/ \____/ \____//_/|_|/____/ \___//_/    \__,_// .___/ \___//_/     
                                                   /_/                   """, "magenta"))
    print("---------------------------------------------------------------------\n")

def get_numeric_input(prompt, min_val=0, max_val=None):
    while True:
        try:
            value = int(input(colored(prompt, "light_blue")))
            if min_val <= value and (max_val is None or value <= max_val):
                return value
            print(colored(f"Invalid input. Please enter a value between {min_val} and {max_val}.", "red"))
        except ValueError:
            print(colored("Invalid input. Please insert a numeric value.", "red"))


# ---- Main area ----------
def stop(code = 0, e = None):
    if code == 0:
        print(f"{colored("PDF saved: ", "green")} {OUTPUT_PDF_PATH}\nPress ENTER to exit")
        web.quit()
        exit(code)        
    if code == 1:
        clear_console()
        print(f"{colored("ERROR: ", "red")}{e}")
        try:
            web.quit()
            delete_temp_dir()
        except Exception:
            pass
        input("Quitting... press ENTER to exit")
        exit(1)
        
def get_configs():
    global OUTPUT_PDF_PATH, CROPPING_RECTANGLE, SLEEP_PAGE_SECONDS, bar, SAVE_CREDENTIALS
    try:
        with open("configs.json", "r") as file:
            f = json.load(file)
        OUTPUT_PDF_PATH = f["output-path"]
        CROPPING_RECTANGLE = f[web.name]["cropping-rectangle"]
        SLEEP_PAGE_SECONDS = f[web.name]["sleep-page-seconds"]
        SAVE_CREDENTIALS = f["save-credentials"]
        bar = ["░" for i in range(f["bar-length"])]
    except FileNotFoundError:
        stop(1, f"Missing congiguration file: {colored("\"configs.json\"", "yellow")}")
    except Exception as e:
        stop(1, f"Error loading configuration file: {e}")
    return f[web.name]["resolution"] 


def progress_bar(progress, total):
    max_icon = int((len(bar) * progress) / total)
    
    for i in range(max_icon):
        bar[i] = colored("█", "magenta")

    percentage = round((100 * progress) / total, 1)
    etc = SLEEP_PAGE_SECONDS*(total -progress)
    if etc >= 3600:
        etc_str = f"{round(etc / 3600,1)} hours"
    elif etc >= 60:
        etc_str = f"{round(etc / 60,1)} minutes"
    else:
        etc_str = f"{round(etc,1)} seconds"
    print(
        f"{colored('Scanning:', 'yellow')} {colored(f'{percentage}%', 'red')}  "
        f"{''.join(bar)} "
        f"[ {colored(progress, 'yellow')} / {colored(total, 'red')} ] pages - {colored("ETC: ", "yellow")}{colored(etc_str, "red")}       ",
        end="\r"
    )
def secure_credential_input(prompt):
    print(prompt, end='', flush=True)
    password = b""
    
    while True:
        char = msvcrt.getch()
        
        if char in {b"\r", b"\n"}: 
            print("")
            break
        elif char == b"\b":  
            password = password[:-1]
            print("\b \b", end='', flush=True)
        elif char == b"\x03": 
            raise KeyboardInterrupt
        else:
            password += char
            print("*", end='', flush=True) 

    return password.decode("utf-8")

def input_handler():
    username, password = credentials.get_credentials(web.name)
    deleted = False
    if  SAVE_CREDENTIALS and username:
        username, password = credentials.get_credentials(web.name)
        if input(colored("NOTICE: ", "yellow")+ "using saved credentials: "+colored("if you want to delete them enter: \"d\"", "magenta")+"\nIf you want to disable credential saving, set \"save-credentials\" in \"configs.json\" to false. \nOtherwise: "+ colored("Press ENTER to continue ", "magenta")).lower() == "d":
            credentials.delete_credentials(web.name)
            clear_console()
            print(colored("Credentials deleted successfully.\n", "green"))
            deleted = True
    if SAVE_CREDENTIALS and (not username or deleted):
        print(f"{colored("NOTICE:", "yellow")} credential saving is set to True. the following credentials will be stored safely,\nIf you want to disable this behavior, set \"save-credentials\" in \"configs.json\" to false.")
    if not username or not SAVE_CREDENTIALS or deleted:
        while True:
            username = secure_credential_input(colored(f"Enter your {web.name} username: ","light_blue"))
            password = secure_credential_input(colored(f"Enter your {web.name} password: ","light_blue"))
            if username and password: break
            clear_console()
            print(colored("Invalid credentials. Please try again.", "red"))
        clear_console()
        if SAVE_CREDENTIALS:
            credentials.save_credentials(web.name ,username, password)
    
    page_number = get_numeric_input(colored("Enter number of pages: ", "light_blue"))
    return username, password, page_number

def select_site():
    print("Select a site")
    for class_ in classes:
        print(f" {colored(classes.index(class_), "red")}: {colored(class_.name, "yellow")}", end = "")
    selected = get_numeric_input(colored("\nEnter site index: ", "light_blue"), 0, len(classes)-1)
    return classes[int(selected)]

def get_img():
    img = Image.open(io.BytesIO(web.take_screenshot()))
    if img.mode in ('RGBA', 'LA'):
        img = img.convert('RGB')
    return img.crop(CROPPING_RECTANGLE)

def gen_pdf(img, x):
    try:
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="PNG")
        img_bytes.seek(0)
        pdf_bytes = img2pdf.convert(img_bytes)
        temp_pdf_path = f"{temp_dir}/temp_{x}.pdf"
        with open(temp_pdf_path, "wb") as temp_pdf:
            temp_pdf.write(pdf_bytes)
        pdf_merger.append(temp_pdf_path)  
    except Exception as e:
        print(f"\n{colored("ERR", "red")}: Failed to process image {x}: {e}")

def delete_temp_dir():
    pdf_merger.close()
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)

def main():
    global web, temp_dir, OUTPUT_PDF_PATH
    temp_dir = f"temp_pdfs_{randint(0, 1000)}"
    clear_console()
    print(f"{colored("Welcome to BookScraper!\n", "green")}")
    web = select_site()
    resolution = get_configs()
    clear_console()
    if not os.path.exists(OUTPUT_PDF_PATH):
        os.makedirs(OUTPUT_PDF_PATH)
    username, password, num_of_pages = input_handler()
    os.mkdir(temp_dir)
    clear_console()
    print("Starting...")
    try:
        web.start(username, password, resolution)
        OUTPUT_PDF_PATH = "\\"+ OUTPUT_PDF_PATH + web.book + ".pdf"
        x = 0
        clear_console()
        while x <= num_of_pages:
            time.sleep(SLEEP_PAGE_SECONDS)
            gen_pdf(get_img() ,x)
            try:
                web.turn_page()
            except Exception as e:
                print(f"{colored("ERROR: ", "red")}, could not turn page, compiling up to page {x}")
                break

            progress_bar(x, num_of_pages)
            x += 1
    
    except Exception as e:
        stop(1, f"An unexpected error occurred: {e}")
    clear_console()
    if os.path.exists(OUTPUT_PDF_PATH):
        if input(colored("WARNING: ", "red") + f" A file with the same name as the output already exists!: " + colored(f"{OUTPUT_PDF_PATH}", "yellow") +  "\ncontinuing would overwrite it. Do you wish to proceed? (y/n): ").lower() == "n":
            exit()
        clear_console()
    print("Merging PDFs...")
    with open(OUTPUT_PDF_PATH, "wb") as pdf_file:
        pdf_merger.write(pdf_file)

    delete_temp_dir()
    web.quit()
    clear_console()
    stop()

if __name__ == "__main__":
    main()