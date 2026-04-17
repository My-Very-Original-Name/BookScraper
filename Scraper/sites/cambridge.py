import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
#local imports
import utils
from base import _Base_web

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
        utils.clear_console()
        print(f"""{utils.color("WARNING:  ", "yellow")} Not all Cambridge-Go books are supported, check on the reader manually, if it's formatted as a scrolling book (one page below the other) it will not be scannable.
              {utils.color("WARNING:  ", "yellow")} Supported books must be already set to the first page""")
        elements = self.driver.find_elements(By.CLASS_NAME, "card-details")
        books = [[utils.color(str(elements.index(element)), "red"), element.text]for element in elements]
        print(utils.selector_table(books))
        i = utils.get_numeric_input("\nInsert book index: ", 0, len(books)-1)
        self.book = elements[i].text
        elements[i].click()
        elements = self.wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "v-card__title")))
        books = [[utils.color(str(elements.index(element)), "red"), element.text]for element in elements]
        utils.clear_console()
        print(utils.selector_table(books))
        i = utils.get_numeric_input("\nInsert book index: ", 0, len(books)-1)
        self.book = self.book + elements[i].text
        elements[i].click()
        time.sleep(1.5)
        self.driver.switch_to.window(self.driver.window_handles[-1])
        print("Waiting for book to load...")
        time.sleep(10)
        utils.clear_console()
        try:
            self.wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "openpageIframe")))
            self.wait.until(EC.frame_to_be_available_and_switch_to_it((By.TAG_NAME, "iframe")))
            self.wait.until(EC.visibility_of_element_located((By.ID, "zoom-singlePage"))).click()
        except Exception:
            utils.stop(self, "Unable to find test element, book may not be supported.")
        
    def turn_page(self):
        self.driver.find_element(By.ID, "next-page-button").click()
            
    def _accept_cookies(self):
        try:
            self.wait.until(EC.presence_of_element_located((By.ID, "onetrust-accept-btn-handler"))).click()
        except Exception:
            pass