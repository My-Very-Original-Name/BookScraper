from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time
#local imports:
import utils
from base import _Base_web

class Mylim(_Base_web):
    def __init__(self):
        self.name = "Loescher(Mylim)"

    def start(self, username, password, resolution):
        self._setup_driver("https://mylim.loescher.it/#!/login", resolution)
        self._enter_credentials(username, password)
        self._select_book()
    
    def _enter_credentials(self, username, password):
        try:
            self.wait.until(EC.presence_of_element_located((By.XPATH, "//button[contains(@class, 'mantine-Button-root') and .//span[text()='Accetta']]"))).click()
        except Exception: pass
        self.wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Nome utente']"))).send_keys(username)
        self.wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Password']"))).send_keys(password)
        button = self.driver.find_element(By.XPATH, "//button[contains(., 'Entra')]")
        self.driver.execute_script("arguments[0].click();", button)

    def _select_book(self):
        time.sleep(2)
        covers = self.wait.until(EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, 'div[class*="volume_copertina"]')
        ))
        titles = self.driver.find_elements(By.CSS_SELECTOR, 'h2[class*="titolo"]')
        books = [[utils.color(str(i), "red"), t.text] for i, t in enumerate(titles)]
        utils.clear_console()
        print(utils.selector_table(books))
        i = utils.get_numeric_input("\nInsert book index: ", 0, len(covers) - 1)
        self.book = titles[i].text
        self.driver.execute_script("arguments[0].click();", covers[i])
        utils.clear_console()
        print("Waiting for book to load...")
        time.sleep(15)
        self.wait.until(EC.presence_of_element_located((By.NAME, "next-page")))
