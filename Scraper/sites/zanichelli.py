from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
#local imports
from Scraper import ui
from .base import _Base_web

class Zanichelli(_Base_web):

    def __init__(self):
        super().__init__()
        self.name = "Zanichelli(Booktab)"
        self.can_run_headless = False

    def _setup_driver(self, url, resolution, window_position):
        self.driver = webdriver.Firefox()
        self.driver.set_window_position(window_position[0], window_position[1])
        self.driver.set_window_size(resolution[0], resolution[1])
        self.driver.get(url)
        self.wait = WebDriverWait(self.driver, 10)

    def start(self, username, password, resolution, window_position = (0,0)):
        self._setup_driver("https://my.zanichelli.it/", resolution, window_position)
        self.enter_credentials(
        username, 
        password,
        username_locator=(By.ID, "modal-username-input"), 
        password_locator=(By.ID, "modal-password-input"), 
        login_btn_locator=(By.CLASS_NAME, "z-button--container"), 
        check_elements=[(By.CSS_SELECTOR, "z-button a[aria-label*='LEGGI EBOOK']")],
        wrong_credentials_elements=[(By.ID, "modal-password-error-box")],
        validate_email=False
        )
        self._accept_cookies()
        self._select_book()

    def _accept_cookies(self):
        try:
            self.wait.until(EC.presence_of_element_located((By.ID, "onetrust-accept-btn-handler"))).click()
        except Exception:
            pass 

    def _delete_devices(self):
        try:
            self.driver.find_element(By.XPATH, "//span[contains(., 'Hai raggiunto il numero massimo')]")
        except Exception as e:
            ui.display_err_and_stop(self, e)
        if ui.generic_user_prompt("Logged devices limit for the website reached. Do you want to remove the latest one to continue?",["y", "n"], show_choices=True, default_choice="y") == "n":
            ui.display_err_and_stop(self,e)
        self.driver.find_element(By.XPATH, "//mat-icon[contains(@class, 'icon-C_notesdelete') and contains(@class, 'pageIcon')]").click()
        self.wait.until(EC.presence_of_element_located((By.XPATH, "//button[.//span[text()='ELIMINA']]"))).click()
        try:
            self._single_page_mode()
        except Exception as e:
            ui.display_err_and_stop(self, e)

    def _single_page_mode(self):
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[title='Impostazioni']"))).click()
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[title='Vista pagina singola (Ctrl + Shift + V)']"))).click()
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[title='Impostazioni']"))).click()

    def check_for_bullshit_popup(self):
        try:
            self.driver.find_element(By.XPATH, "//button[normalize-space(text())='Chiudi']").click()
        except Exception: pass

    def _select_book(self):
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "z-button a[aria-label*='LEGGI EBOOK']")))
        buttons = self.driver.find_elements(By.CSS_SELECTOR, "z-button a[aria-label*='LEGGI EBOOK']")

        books = []
        for i, btn in enumerate(buttons):
            full_label = btn.get_attribute("aria-label")
            clean_title = full_label.split("LEGGI EBOOK")[-1].split(",")[0].strip()
            books.append(clean_title)

        ui.clear_console()
        ui.print_reminder("Books must be already set to double page mode and to the first page")
        ui.print_reminder("Zanichelli does not work in headless mode, if you see a browser window do not resize, close or minimize it.")

        i = ui.print_selector_table(books)
        self.book = buttons[i].get_attribute("aria-label").split("LEGGI EBOOK")[-1].strip()
        buttons[i].click()
        self.driver.switch_to.window(self.driver.window_handles[1])

        ui.clear_console()
        print("waiting for book to load...")
        time.sleep(5)

        try:
            self._single_page_mode()

        except Exception:
            ui.clear_console()
            self._delete_devices()
        time.sleep(3)


    def turn_page(self):
        self.check_for_bullshit_popup()
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Avanti']"))).click()
