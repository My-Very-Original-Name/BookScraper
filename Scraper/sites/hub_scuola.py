import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
#local imports
from base import _Base_web
import utils

class Hub_scuola(_Base_web):
    def __init__(self):
        self.name = "Hub-Scuola"

    def start(self, username, password, resolution):
        self._setup_driver("https://www.hubscuola.it/login", resolution)
        self._accept_cookies()
        self._enter_credentials(username, password)
        utils.clear_console()
        self._select_book()
        utils.clear_console()
        self._select_book2()
        utils.clear_console()
        self._select_edition()

    def _enter_credentials(self, username, password):
        self.wait.until(EC.presence_of_element_located((By.NAME, "username"))).send_keys(username)
        self.driver.find_element(By.NAME, "password").send_keys(password)
        self.driver.find_elements(By.XPATH, "//button//span[text()='Accedi']")[0].click()
        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME,"R7FWxhKTRu2I206FyL0A")))
    
    def _select_book(self):
        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "zW9ivNHXZ2LXEAF2iGDo")))
        elements = self.driver.find_elements(By.CLASS_NAME, "zW9ivNHXZ2LXEAF2iGDo")
        buttons = self.driver.find_elements(By.XPATH, "//button//span[text()='Esplora']")
        books = [[utils.color(str(elements.index(element)), "red"), element.text[:50]]for element in elements]
        print(f"{utils.color("WARNING:  ", "yellow")}Books must be already set to the first page")
        print(utils.selector_table(books))
        i = utils.get_numeric_input("\nInsert book index: ", 0, len(elements) - 1)
        self.book = elements[i].text
        buttons[i].click()
    
    def _select_book2(self):
        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "LA0in5eDCqmqYQn79QwT")))
        elements = self.driver.find_elements(By.CLASS_NAME, "LA0in5eDCqmqYQn79QwT")
        elements = elements[5:]
        books = [[utils.color(str(elements.index(element)), "red"), element.text[:50]]for element in elements]
        print(f"{utils.color("WARNING:  ", "yellow")}Books must be already set to the first page")
        print(f"""{utils.color("WARNING: ", "yellow")}The following selection might not only contain books, plase only select textbooks.\nselecting other items will result in unexpected behavior.\n""")
        print(utils.selector_table(books))
        i = utils.get_numeric_input("\nInsert book index: ", 0, len(elements) - 1)
        elements[i].click()
    
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
        books = [[utils.color(str(first_type_links.index(element)), "red"), element.text[:50]]for element in first_type_links]
        print(utils.selector_table(books))
        i = utils.get_numeric_input("\nInsert book index: ", 0, len(first_type_links) - 1)
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
        self.wait.until(EC.presence_of_element_located((By.ID, "pspdfkit-next-page"))).click()
    
    def check_load(self):
        self.wait.until(EC.element_to_be_clickable((By.ID, "pspdfkit-next-page")))