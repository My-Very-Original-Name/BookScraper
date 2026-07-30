from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time
#local imports:
from Scraper import ui
from .base import _Base_web

class Mylim(_Base_web):
    def __init__(self):
        super().__init__()
        self.name = "Loescher(Mylim)"

    def start(self, username, password, resolution):
        self._setup_driver("https://mylim.loescher.it/#!/login", resolution)
        self._accept_cookies()
        self.enter_credentials(
            username, 
            password, 
            username_locator=(By.XPATH, "//input[@placeholder='Nome utente']"), 
            password_locator=(By.XPATH, "//input[@placeholder='Password']"), 
            login_btn_locator=(By.XPATH, "//button[contains(., 'Entra')]") )
        #self._enter_credentials(username, password)
        self._select_book()

    def _accept_cookies(self):
        try:
            self.wait.until(EC.presence_of_element_located((By.XPATH, "//button[contains(@class, 'mantine-Button-root') and .//span[text()='Accetta']]"))).click()
        except Exception: pass

    def _enter_credentials(self, username, password):

        self.wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Nome utente']"))).send_keys(username)
        self.wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Password']"))).send_keys(password)
        button = self.driver.find_element(By.XPATH, "//button[contains(., 'Entra')]")
        self.driver.execute_script("arguments[0].click();", button)

    def _select_book(self):
        time.sleep(2)
        covers = self.wait.until(EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, 'div[class*="volume_copertina"]')
        ))
        books = self.driver.find_elements(By.CSS_SELECTOR, 'h2[class*="titolo"]')
        titles = [book.text for book in books]
        ui.clear_console()
        i = ui.print_selector_table(titles)
        self.book = titles[i]
        self.driver.execute_script("arguments[0].click();", covers[i])
        ui.clear_console()
        print("Waiting for book to load...")
        time.sleep(15)
        self.wait.until(EC.presence_of_element_located((By.NAME, "next-page")))
    
    def turn_page(self):
        self.wait.until(EC.presence_of_element_located((By.NAME, "next-page"))).click()
