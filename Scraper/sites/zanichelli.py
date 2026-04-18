from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
#local imports
from Scraper import utils
from .base import _Base_web

class Zanichelli(_Base_web):

    def __init__(self):
        self.name = "Zanichelli(Booktab)"
    def _setup_driver(self, url, resolution):
        self.driver = webdriver.Firefox()
        self.driver.set_window_size(resolution[0], resolution[1])
        self.driver.get(url)
        self.wait = WebDriverWait(self.driver, 10)

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
        time.sleep(1)

    def _accept_cookies(self):
        try:
            self.wait.until(EC.presence_of_element_located((By.ID, "onetrust-accept-btn-handler"))).click()
        except Exception:
            pass 
    def _delete_devices(self):
        try:
            self.driver.find_element(By.XPATH, "//span[contains(., 'Hai raggiunto il numero massimo')]")
        except Exception as e:
            utils.stop(self, e)
        if input(f"{utils.color("WARNING: ", "yellow")}Logged devices limit for the website reached. Do you want to remove the latest one to continue? (y,n): ").lower() == "n":
            utils.stop(self,e)
        self.driver.find_element(By.XPATH, "//mat-icon[contains(@class, 'icon-C_notesdelete') and contains(@class, 'pageIcon')]").click()
        self.wait.until(EC.presence_of_element_located((By.XPATH, "//button[.//span[text()='ELIMINA']]"))).click()
        try:
            self._single_page_mode()
        except Exception as e:
            utils.stop(self, e)
    def _single_page_mode(self):
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[title='Impostazioni']"))).click()
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[title='Vista pagina singola (Ctrl + Shift + V)']"))).click()
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[title='Impostazioni']"))).click()
    def check_for_bullshit_popup(self):
        try:
            self.driver.find_element((By.XPATH, "//button[normalize-space(text())='Chiudi']")).click()
        except Exception: pass

    def _select_book(self):
        buttons = self.driver.find_elements(By.CSS_SELECTOR, "z-button a[aria-label*='LEGGI EBOOK']")
        books = []
        for i, btn in enumerate(buttons):
            full_label = btn.get_attribute("aria-label")
            clean_title = full_label.split("LEGGI EBOOK")[-1].split(",")[0].strip()       
            books.append([utils.color(str(i), "red"), clean_title])

        utils.clear_console()
        print(f"{utils.color("WARNING: ", "yellow")}books must already be set to double page mode and to the firts page")
        print(f"{utils.color("WARNING: ", "yellow")}do not resize, close or minimize the browser window")
        print(utils.selector_table(books))
        i = utils.get_numeric_input("\nInsert book index: ", 0, len(buttons) - 1)
        self.book = buttons[i].get_attribute("aria-label").split("LEGGI EBOOK")[-1].strip()
        buttons[i].click()
        self.driver.switch_to.window(self.driver.window_handles[1])
        utils.clear_console()
        print("waiting for book to load...")
        time.sleep(5)
        try:
            self._single_page_mode()
        except Exception:
            utils.clear_console()
            self._delete_devices()
        time.sleep(3)


    def turn_page(self):
        self.check_for_bullshit_popup()
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Avanti']"))).click()
