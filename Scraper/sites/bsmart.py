import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
#local imports
import utils
from base import _Base_web

class Bsmart(_Base_web):
    def __init__(self):
        self.name = "Bsmart"

    def start(self, username, password, resolution):
        self._setup_driver("https://www.bsmart.it/users/sign_in", resolution)
        self._enter_credentials(username, password)
        self._select_book()

    def _enter_credentials(self, username, password):
        self.wait.until(EC.presence_of_element_located((By.ID, "user_email"))).send_keys(username) 
        self.driver.find_element(By.ID, "user_password").send_keys(password)
        self.driver.find_element(By.NAME, "commit").click()
    
    def _accept_cookies(self):
        try:
            time.sleep(2)
            self.driver.find_element(By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll").click()
        except Exception as e:
            pass
    
    def _select_book(self):
        self.wait.until(EC.presence_of_element_located((By.LINK_TEXT, "BSMART BOOKS"))).click()
        self.driver.switch_to.window(self.driver.window_handles[1])
        self.wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/books/')]")))
        self._accept_cookies()
        elements = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/books/'][data-discover='true']")
        titles = []
        elements_text = []
        for element in elements:
            if element.text:
                titles.append(element.text)
            elements_text.append(element.text)
        books = [[utils.color(str(i), "red"), title] for i, title in enumerate(titles)]
        utils.clear_console()
        print(f"{utils.color("WARNING: ", "red")}Books must be already set to the first page")
        print(utils.selector_table(books))
        i = utils.get_numeric_input("\nInsert book index: ", 0, len(elements) - 1)
        i = elements_text.index(titles[i])
        self.book = elements[i].text
        elements[i].click()
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "button[title='Vai alla pagina successiva']")))
        self.driver.find_elements(By.CSS_SELECTOR, "button[aria-pressed='false'].inline-flex.items-center.justify-center.h-fit")[4].click()
        self.driver.find_element(By.XPATH, "//li[contains(@class, 'dark:text-white') and contains(., 'Disposizione pagine')]").find_element(By.XPATH, ".//button[contains(@class, 'inline-flex')]").click()
        button = self.driver.find_elements(By.XPATH, "//button[contains(@class, 'inline-flex')]")[6]
        self.driver.execute_script("arguments[0].click();", button)
    
    def turn_page(self):
        self.driver.find_element(By.CSS_SELECTOR, "button[title='Vai alla pagina successiva'].flex.justify-center.items-center.absolute").click()