from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re

class InvalidLoginError(Exception): pass

class _Base_web():
    def __init__(self) -> None:
        self.can_run_headless = True
        self.virtual_display = None
        
    def take_screenshot(self) -> None:
        return self.driver.get_screenshot_as_png()

    def quit(self) -> None:
        self.driver.quit()
        if self.virtual_display:
            self.virtual_display.stop()
   
    def _login_outcome(self, check_elements:list, wrong_credentials_elements:list):
        """wrong_credentials_elements ans check_elements: list of elements (tuples), if one is found the login is flagged as failed"""
        if check_elements:
            for element in check_elements:
                if self.driver.find_elements(*element):
                    return "success"

        if wrong_credentials_elements:
            for element in wrong_credentials_elements:
                if self.driver.find_elements(*element):
                    return "error"
        return False

    def _is_valid_email(self, email: str) -> bool:
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        
        return bool(re.match(pattern, email))
    
    def enter_credentials(
        self,
        user_name: str,
        password: str,
        username_locator: tuple,
        password_locator: tuple,
        login_btn_locator: tuple,
        check_elements: tuple,
        wrong_credentials_elements: list = None,
        validate_email: bool = True
    ) -> None:
        """wrong_credentials_elements: list of elements (tuples), if one is found the login is flagged as failed"""

        if validate_email:
            if not self._is_valid_email(user_name): raise InvalidLoginError

        self.wait.until(EC.presence_of_element_located(username_locator)).send_keys(user_name)
        self.wait.until(EC.presence_of_element_located(password_locator)).send_keys(password) 
        self.wait.until(EC.presence_of_element_located(login_btn_locator)).click()
        
        time.sleep(1)

        outcome = self.wait.until(lambda driver: self._login_outcome(check_elements, wrong_credentials_elements))
        if outcome == "error":
            raise InvalidLoginError("Failed login attempt detected")


    def _setup_driver(self, url, resolution) -> None:
        options = Options()
        options.add_argument("--headless")

        options.set_preference("layout.css.devPixelsPerPx", "1.0") 
        options.set_preference("browser.zoom.siteSpecific", False)  
        options.set_preference("apz.allow_zooming", False)  
        
        self.driver = webdriver.Firefox(options=options)
        self.driver.set_window_size(resolution[0], resolution[1]) 
        self.driver.get(url)
        self.driver.execute_script("""
        // Lock zoom to 100%
        document.body.style.zoom = '1';
        
        // Override window.onload
        const originalOnLoad = window.onload;
        window.onload = function() {
            document.body.style.zoom = '1';
            if (originalOnLoad) originalOnLoad.apply(this, arguments);
        };
        
        // Override history API (for SPAs)
        const originalPushState = history.pushState;
        history.pushState = function() {
            originalPushState.apply(this, arguments);
            document.body.style.zoom = '1';
        };
        
        // Add viewport meta tag
        const meta = document.createElement('meta');
        meta.name = 'viewport';
        meta.content = 'width=device-width, initial-scale=1, maximum-scale=1, user-scalable=0';
        document.head.appendChild(meta);
        """)
        self.wait = WebDriverWait(self.driver, 10)