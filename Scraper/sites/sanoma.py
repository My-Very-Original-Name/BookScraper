from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
import time
#local imports
from Scraper import ui
from .base import _Base_web

class Sanoma(_Base_web):
    def __init__(self):
        super().__init__()
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
        except:
            pass

        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "product-title")))
        elements = self.driver.find_elements(By.CLASS_NAME, "product-title")
        books_elements = [e for e in elements if len(e.text.strip()) > 0]
        titles = [book.text for book in books_elements]

        ui.clear_console()
        ui.print_reminder("Books must be set to the first page")
        idx = ui.print_selector_table(titles)
        target_book_element = books_elements[idx]
        self.book = target_book_element.text
        target_book_element.click()

        try:
            try:
                annuity_selector = "ul.annuities-list li.annuity button"
                self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".annuities-list")))
                annuities = self.driver.find_elements(By.CSS_SELECTOR, annuity_selector)

                if annuities:
                    annuities_text = [annuity.text.strip() for annuity in annuities]
                    ui.clear_console()
                    ui.print_reminder("Books must be set to the first page")
                    a_idx = ui.print_selector_table(annuities_text)
                    annuities[a_idx].click()
            except:
                pass

            volume_selector = "div.clamp-4" 
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, volume_selector)))
            vols = self.driver.find_elements(By.CSS_SELECTOR, volume_selector)
            vol_texts = [vol.text.strip() for vol in vols]

            ui.clear_console()
            ui.print_reminder("Books must be set to the first page")
            v_idx = ui.print_selector_table(vol_texts)
            vols[v_idx].click()

        except Exception as e:
            ui.display_err_and_stop(self, f"Errore nella selezione volume: {e}")
            
        self.driver.switch_to.window(self.driver.window_handles[-1])
        ui.clear_console()
        print("Waiting for book to load...")
        self.wait.until(EC.frame_to_be_available_and_switch_to_it((By.TAG_NAME, "iframe")))
        try:
            self.wait.until(EC.element_to_be_clickable((By.ID, "ppms_cm_agree-to-all"))).click()
            self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[title='Pagina singola']"))).click()
        except:
            pass
    
    def turn_page(self):
        self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Pagina seguente']"))).click()