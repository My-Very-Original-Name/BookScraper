import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
#local imports
from Scraper import ui
from .base import _Base_web, InvalidLoginError

class Cambridge(_Base_web):
    def __init__(self):
        super().__init__()
        self.name = "Cambridge"

    def start(self, username, password, resolution):
        self._setup_driver("https://www.cambridge.org/go/login", resolution)
        self.enter_credentials(username, password)
        self._select_book()
    
    def enter_credentials(self, username, password):
        self._accept_cookies()
        time.sleep(1.5)
        
        self.wait.until(EC.presence_of_element_located((By.ID, "gigya-loginID-75570100315269100"))).send_keys(username)
        self.driver.find_elements(By.CLASS_NAME, "gigya-input-submit")[6].click()
        outcome = self.wait.until(lambda driver: self._login_outcome(check_elements =[(By.ID, "gigya-password-28556111034728640")], wrong_credentials_elements = [(By.ID, "gigya-error-msg-gigya-passwordless-login-form-loginID")]))
        if outcome == "error":
            raise InvalidLoginError
        
        self.wait.until(EC.presence_of_element_located((By.ID, "gigya-password-28556111034728640"))).send_keys(password)
        self.driver.find_elements(By.CLASS_NAME, "gigya-input-submit")[6].click()
        outcome = self.wait.until(lambda driver: self._login_outcome(check_elements = [(By.CLASS_NAME, "card-title"), (By.ID, "gigya-checkbox-6926267525994684")], wrong_credentials_elements = [(By.CSS_SELECTOR, "div.gigya-error-code-403042")]))
        if outcome == "error":
            raise InvalidLoginError
        
        try:
            self.wait.until(EC.presence_of_element_located((By.ID, "gigya-checkbox-6926267525994684"))).click()
            self.wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='submit'][@value='Get started with GO']"))).click()
            time.sleep(2)
        except:
            pass

        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "card-title")))

    def _select_book(self):
        ui.clear_console()
        ui.print_reminder("Not all Cambridge-Go books are supported, check on the reader manually, if it's formatted as a scrolling book (one page below the other) it will not be scannable.")
        ui.print_reminder("Books must be already set to the first page")

        elements = self.driver.find_elements(By.CLASS_NAME, "card-details")
        time.sleep(2)
        i = ui.print_selector_table([element.text for element in elements])
        self.book = elements[i].text
        elements[i].click()
        
        elements = self.wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "v-card__title")))
        ui.clear_console()
        i = ui.print_selector_table([element.text for element in elements])
        self.book = self.book + elements[i].text
        elements[i].click()
        time.sleep(1.5)
        
        self.driver.switch_to.window(self.driver.window_handles[-1])
        ui.clear_console()
        print("Waiting for book to load...")
        time.sleep(10)
        ui.clear_console()
        try:
            self.wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "openpageIframe")))
            self.wait.until(EC.frame_to_be_available_and_switch_to_it((By.TAG_NAME, "iframe")))
            self.wait.until(EC.visibility_of_element_located((By.ID, "zoom-singlePage"))).click()
        except Exception:
            ui.display_err_and_stop(self, "Unable to find test element, book is not supported.")
        
    def turn_page(self):
        self.driver.find_element(By.ID, "next-page-button").click()
            
    def _accept_cookies(self):
        try:
            self.wait.until(EC.presence_of_element_located((By.ID, "onetrust-accept-btn-handler"))).click()
        except Exception:
            pass