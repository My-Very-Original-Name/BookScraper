import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
#local imports
from Scraper import ui
from .base import _Base_web

class Hub_scuola(_Base_web):
    def __init__(self):
        super().__init__()
        self.name = "Hub-Scuola"

    def start(self, username, password, resolution):
        self._setup_driver("https://www.hubscuola.it/login", resolution)
        self._accept_cookies()
        self.enter_credentials(
            username, 
            password, 
            username_locator=(By.NAME, "username"), 
            password_locator=(By.NAME, "password"), 
            login_btn_locator=(By.XPATH, "//button//span[text()='Accedi']"), 
            check_elements=[(By.CLASS_NAME, "XZWhLi22KkhBjwHCUUyw")], 
            wrong_credentials_elements=[(By.ID, "login-error")]
        )
        ui.clear_console()
        self._select_book()
        ui.clear_console()
        self._select_book2()
        ui.clear_console()
        self._select_edition()
    
    def _select_book(self):
        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "XZWhLi22KkhBjwHCUUyw")))
        containers = self.driver.find_elements(By.CLASS_NAME, "XZWhLi22KkhBjwHCUUyw")
        books = []
        buttons = []
        for i, item in enumerate(containers):
            title_el = item.find_element(By.CLASS_NAME, "zW9ivNHXZ2LXEAF2iGDo")
            button_el = item.find_element(By.XPATH, ".//a[.//span[contains(text(), 'Esplora')]]")
            books.append(title_el.text[:70])
            buttons.append(button_el)

        ui.print_reminder("Books must be already set to the first page")
        choice = ui.print_selector_table(books)
        self.book = books[choice][1]
        buttons[choice].click()
    
    def _select_book2(self):
        selector = "swiper-container .LA0in5eDCqmqYQn79QwT"
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))

        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
        books_elements = [e for e in elements if "CONTENUTI DI ESEMPIO" not in e.text.upper()]

        ui.print_reminder("Books must be already set to the first page")
        i = ui.print_selector_table([e.text[:70] for e in books_elements])
        books_elements[i].click()
    
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

        books = [element.text[:70]for element in first_type_links]
        ui.print_reminder("Books must be already set to the first page")
        i = ui.print_selector_table(books)

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