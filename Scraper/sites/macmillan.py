import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
import io
#local imports
from Scraper import ui
from .base import _Base_web

class Macmillan(_Base_web):
    def __init__(self):
        super().__init__()
        self.name = "Macmillan"
        self.last_scanned_left_double_page = False
        self.cropping_rectangle = None
    
    def start(self, username, password, resolution) -> None:
        self._setup_driver("https://www.macmillaneducationeverywhere.com/oidc-login", resolution)
        self.enter_credentials(
            username, 
            password, 
            username_locator=(By.ID, "username"), 
            password_locator=(By.ID, "password"), 
            login_btn_locator=(By.CSS_SELECTOR, "button.u-button.u-button-full-width.u-button--primary[type='submit']"),
            check_elements=[(By.ID, "skiptocontent")], 
            wrong_credentials_elements=[(By.ID, "LoginErrorValidation_errors-list")],
            validate_email=False
        )
        self._clear_cookies()
        self._select_book()
    
    def _select_book(self) -> None:
        books = self.driver.find_elements(By.CSS_SELECTOR, ".c-book-tile__footer.u-small-text")
        if not books: ui.display_err_and_stop(self, "No books found")

        titles = [book.text for book in books]

        ui.clear_console()
        ui.print_reminder("Books must be already set to the first page")

        i = ui.print_selector_table(titles)
        
        books[i].click()
        self.book = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.u-button.u-button--primary.arrow-next"))).click()
        time.sleep(2)
        self.book = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.u-button.u-button--primary.view-link--button"))).click()
        time.sleep(2)
        self.driver.switch_to.window(self.driver.window_handles[1])
        self._dismiss_popups()
        self.book = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "series-group__title"))).text
        
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".series-group__resources-list-item a.c-card__link")))
        self.driver.find_element(By.CSS_SELECTOR, ".series-group__resources-list-item a.c-card__link").click()
        
        self.wait.until(EC.presence_of_element_located((By.ID, "viewer")))

    def _clear_cookies(self):
        try:
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "button[data-cc-action='reject']"))).click()
        except Exception:
            pass
    def _dismiss_popups(self) -> None:

        self._clear_cookies()
        
        #keep logged in prompt        
        try:
            self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".loader")))
            self.wait.until(EC.element_to_be_clickable((By.ID, "Yes"))).click()
        except Exception:
            pass
        #onboarding
        try:
            self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".loader")))
            self.wait.until(EC.element_to_be_clickable((By.ID, "skip-onboarding-modal"))).click()
        except Exception:
            pass
    
    def take_screenshot(self):
        
        self._hide_next_page_tooltip()
        base_img_bytes = self.driver.get_screenshot_as_png()

        if self.driver.find_elements(By.CLASS_NAME, "fixed-page-frame-center"): 
            return base_img_bytes
        
        elif not self.cropping_rectangle:
            ui.display_err_and_stop(self, "Could not find single page to use as a template for cropping, please restart the scan on a single page.")
        
        base_img = Image.open(io.BytesIO(base_img_bytes))

        offset = int((self.cropping_rectangle[2] - self.cropping_rectangle[0])/2)
        if not self.last_scanned_left_double_page:
            
            self.last_scanned_left_double_page = True
            return self._image_to_bytes(self._pad_image_left(base_img, offset))
        
        self.last_scanned_left_double_page = False
        return self._image_to_bytes(self._crop_from_left(base_img, offset))
    
    def _image_to_bytes(self, img):
        output = io.BytesIO()
        img.save(output, format="PNG")
        return output.getvalue()

    def turn_page(self):
        if self.last_scanned_left_double_page:
            return
        
        error = None
        for attempt in range(5):
            try:
                self.driver.find_element(By.ID, "nextButtonFullScreen").click()
                self.wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, ".loader")))
                return
            except Exception as e:
                error = e
                time.sleep(1)
        ui.display_err_and_stop(self, error)
        
    def _crop_from_left(self, img, offset_px):
        return img.crop((offset_px, 0, img.width, img.height))

    def _pad_image_left(self, img,  offset_px):
        padded = Image.new(img.mode, (img.width + offset_px, img.height),(255,255,255))
        padded.paste(img, (offset_px, 0))
        
        return padded
    
    def _hide_next_page_tooltip(self):
        self.driver.execute_script(
            "document.querySelectorAll('maced-tooltip').forEach(e => e.style.display = 'none');"
        )