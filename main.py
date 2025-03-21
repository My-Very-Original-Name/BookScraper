from PIL import Image
import img2pdf
import io
import time
from PyPDF2 import PdfMerger
import os
import shutil
import ctypes    
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


# ---- Classes ----
class Zanichelli:
    """Handles interactions with the Zanichelli website"""
    def __init__(self):
        self.name = "Zanichelli"
        self.cropping_rectangle = [1189, 50, 2684, 2066]

    def start(self, username, password, resolution):
        """Logs into Zanichelli and selects a book"""
        options = Options()
        options.headless = True
        self.driver = webdriver.Firefox(options=options)
        self.driver.set_window_size(resolution[0], resolution[1])
        self.driver.get("https://my.zanichelli.it/home")
        self.wait = WebDriverWait(self.driver, 10)

        # Login
        self._enter_credentials(username, password)
        self._accept_cookies()
        self._select_book()

    def _enter_credentials(self, username, password):
        """Enter login credentials"""
        email_input = self.wait.until(EC.presence_of_element_located((By.ID, "inline-username-input")))
        password_input = self.driver.find_element(By.ID, "inline-password-input")

        email_input.send_keys(username)
        password_input.send_keys(password)

        self.driver.find_element(By.CLASS_NAME, "z-button--container").click()
        self.wait.until(EC.presence_of_element_located((By.ID, "home")))

    def _accept_cookies(self):
        """Accepts cookie popup if present"""
        try:
            self.wait.until(EC.presence_of_element_located((By.ID, "onetrust-accept-btn-handler"))).click()
        except Exception:
            pass  # No cookie popup detected

    def _select_book(self):
        """Selects a book from the list"""
        buttons = self.driver.find_elements(By.CSS_SELECTOR, "button[aria-label*='LEGGI EBOOK']")
        books = [[colored(str(i), "red"), btn.get_attribute("aria-label").split("LEGGI EBOOK")[-1].strip()] for i, btn in enumerate(buttons)]

        clear_console()
        print(tabulate(books, headers=['Index', 'Name'], tablefmt='pipe', colalign=("center", "center")))
        i = get_numeric_input("\nInsert book index: ", 0, len(buttons) - 1)
        
        buttons[i].click()
        self.driver.switch_to.window(self.driver.window_handles[1])
        time.sleep(5)  # Wait for book to load
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "button[aria-label='Vista pagina singola (Ctrl + Shift + V)']"))).click()

    def turn_page(self):
        """Turns the book page"""
        self.wait.until(EC.presence_of_element_located((By.ID, "default_next_bttn"))).click()

    def take_screenshot(self):
        """Takes a screenshot of the book"""
        return self.driver.get_screenshot_as_png()

    def quit(self):
        """Closes the browser"""
        self.driver.quit()

class Hub_scuola():
    def __init__(self):
        self.name = "Hub-Scuola"
        self.cropping_rectangle = ()

    def start(self, username, password, resolution):
        options = Options()
        options.headless = True
        self.driver = webdriver.Firefox(options=options)
        self.driver.set_window_size(resolution[0], resolution[1])
        self.driver.get("https://www.hubscuola.it/login")
        self.wait = WebDriverWait(self.driver, 10)
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
            pass  # No cookie popup detected
    def turn_page(self):
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.g-btn-page.g-btn-page--next"))).click()
    def take_screenshot(self):
        """Takes a screenshot of the book"""
        return self.driver.get_screenshot_as_png()

    def quit(self):
        """Closes the browser"""
        self.driver.quit()

# ---- Global variables ----
classes = [Zanichelli(), Hub_scuola()]
pdf_merger = PdfMerger()


# ---- Helper functions -------------------------------
def clear_console():
    """Clears the terminal screen"""
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
    """Ensures numeric input within a valid range"""
    while True:
        try:
            value = int(input(colored(prompt, "light_blue")))
            if min_val <= value and (max_val is None or value <= max_val):
                return value
            print(colored(f"Invalid input. Please enter a value between {min_val} and {max_val}.", "red"))
        except ValueError:
            print(colored("Invalid input. Please insert a numeric value.", "red"))

# ---- Main area ----------
def get_configs():
    global OUTPUT_PDF_PATH, CROPPING_RECTANGLE, SLEEP_PAGE_SECONDS, bar
    with open("configS.json", "r") as file:
        f = json.load(file)
    OUTPUT_PDF_PATH = f["output-path"]
    CROPPING_RECTANGLE = f[web.name]["cropping-rectangle"]
    SLEEP_PAGE_SECONDS = f["sleep-page-seconds"]
    bar = ["░" for i in range(f["bar-length"])] 
    return f[web.name]["resolution"] 

def progress_bar(progress, total):
    max_icon = int((len(bar) * progress) / total)
    
    for i in range(max_icon):
        bar[i] = colored("█", "magenta")

    percentage = round((100 * progress) / total, 1)
    etc = SLEEP_PAGE_SECONDS*(total -progress)
    if etc >= 3600:
        etc_str = f"{etc // 3600} hours"
    elif etc >= 60:
        etc_str = f"{etc // 60} minutes"
    else:
        etc_str = f"{etc} seconds"
    print(
        f"{colored('Scanning:', 'yellow')} {colored(f'{percentage}%', 'red')}  "
        f"{''.join(bar)} "
        f"[ {colored(progress, 'yellow')} / {colored(total, 'red')} ] pages - {colored("ETC: ", "yellow")}{colored(etc_str, "red")}",
        end="\r"
    )
def secure_credential_input(prompt):
    """Securely handles credentials input"""
    print(prompt, end='', flush=True)
    password = b""
    
    while True:
        char = msvcrt.getch()
        
        if char in {b"\r", b"\n"}:  # Enter key
            print("")
            break
        elif char == b"\b":  # Backspace
            password = password[:-1]
            print("\b \b", end='', flush=True)
        elif char == b"\x03":  # Ctrl+C
            raise KeyboardInterrupt
        else:
            password += char
            print("*", end='', flush=True)  # Mask input with *

    return password.decode("utf-8")

def input_handler():
    username = secure_credential_input(colored(f"Enter your {web.name} username: ","light_blue"))
    password = secure_credential_input(colored(f"Enter your {web.name} password: ","light_blue"))
    clear_console()
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
        print(f"{colored("ERR", "red")}: Failed to process image {x}: {e}")

def main():
    global web, temp_dir
    temp_dir = f"temp_pdfs_{randint(0, 1000)}"
    clear_console()
    print(f"{colored("Welcome to BookScraper!\n", "green")}")
    web = select_site()
    resolution = get_configs()
    print(resolution)
    clear_console()
    if os.path.exists(OUTPUT_PDF_PATH):
        if input(colored("WARNING: ", "red") + f" A file with the same name as the output already exists!: " + colored(f"{OUTPUT_PDF_PATH}", "yellow") +  "\ncontinuing would overwrite it. Do you wish to proceed? (y/n): ").lower() == "n":
            exit()
        clear_console()
    username, password, num_of_pages = input_handler()
    os.mkdir(temp_dir)
    clear_console()
    print("Starting...")
    try:
        web.start(username, password, resolution)
        x = 0
        clear_console()
        while x <= num_of_pages:
            time.sleep(SLEEP_PAGE_SECONDS)
            gen_pdf(get_img() ,x)
            web.turn_page()

            progress_bar(x, num_of_pages)
            x += 1
    
    except Exception as e:
        print(f"{colored("ERROR", "red")} An unexpected error occurred: {e}")
        web.quit()
        exit(1)
    clear_console()
    print("Merging PDFs...")
    with open(OUTPUT_PDF_PATH, "wb") as pdf_file:
        pdf_merger.write(pdf_file)

    pdf_merger.close()
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    web.quit()
    clear_console()
    print(f"{colored("PDF saved: ", "green")} {OUTPUT_PDF_PATH}\nPress ENTER to exit")

if __name__ == "__main__":
    main()