from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
import time
#local imports
from Scraper import utils
from .base import _Base_web

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
        self.wait.until(EC.element_to_be_clickable((By.NAME, "password"))).send_keys(password)
        self.driver.find_element(By.NAME, "submit").click()
    
    def _accept_cookies(self):
        try:
            self.driver.find_element(By.ID, "ppms_cm_agree-to-all").click()
            self.wait.until(EC.presence_of_element_located((By.ID, "ppms_consent_form_success_note_button"))).click()
        except Exception:
            pass
    
    def _select_book(self):
        self.wait.until(EC.presence_of_element_located((By.XPATH, "//a[@href='/prodotti_digitali']"))).click()
        try:
            self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[title="Chiudi modale"]'))).click()
        except Exception:
            pass
        self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "product-title")))
        elements = self.driver.find_elements(By.CLASS_NAME, "product-title")
        books = [[utils.color(i, "red"), element.text] for i, element in enumerate(elements)]
        utils.clear_consoleclear_console()
        print(f"{utils.color("WARNING:  ", "yellow")}Books must be already set to the first page")
        print(utils.selector_table(books))
        elements[utils.get_numeric_input("\nInsert book index: ", 0, len(elements) - 1)].click()
        try:
            elements = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'anno')]")))
            options = [[utils.colored(i, "red"), element.text] for i, element in enumerate(elements)]
            utils.clear_console()
            print(f"{utils.color("WARNING: ", "red")}Books must be already set to the first page")
            print(utils.selector_table(options))
            elements[utils.get_numeric_input("\nInsert year index: ", 0, len(elements) - 1)].click()
        except Exception:
            pass
        elements = self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.clamp-4.f-1.svelte-1wrsvtu")))
        books = [[utils.color(i, "red"), element.text] for i, element in enumerate(elements)]
        utils.clear_console()
        print(f"{utils.color("WARNING:  ", "yellow")}Books must be already set to the first page")
        print(utils.selector_table(books))
        i = utils.get_numeric_input("\nInsert book index: ", 0, len(elements) - 1)
        elements[i].click()
        self.book = elements[i].text
        self.driver.switch_to.window(self.driver.window_handles[1])
        utils.clear_console()
        print("Waiting for book to load...")
        time.sleep(7)
        self.wait.until(EC.frame_to_be_available_and_switch_to_it((By.TAG_NAME, "iframe")))
        self.driver.find_element(By.CSS_SELECTOR, "span.icon.icon-page-single").click()
        self.driver.find_element(By.ID, "page-field").send_keys("1")
        self.driver.find_element(By.ID, "page-field").send_keys(Keys.ENTER)
    
    def turn_page(self):
        self.wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@class, 'turn-page right')]"))).click()