from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class InvalidLoginError(Exception): pass

class _Base_web():
    def __init__(self):
        self.can_run_headless = True
        self.virtual_display = None
        
    def take_screenshot(self):
        return self.driver.get_screenshot_as_png()

    def quit(self):
        self.driver.quit()
        if self.virtual_display:
            self.virtual_display.stop()

    def enter_credentials(
        self,
        usernmame: str,
        password: str,
        username_locator: tuple,
        password_locator: tuple,
        login_btn_locator: tuple,
        timeout: float = 0,
        check_element: tuple = None,
        wrong_credentials_element: tuple = None
    ) -> None:
        
        self.wait.until(EC.presence_of_element_located(username_locator)).send_keys(usernmame)
        self.wait.until(EC.presence_of_element_located(password_locator)).send_keys(password) 
        self.wait.until(EC.presence_of_element_located(login_btn_locator)).click()
        
        time.sleep(1)

        if wrong_credentials_element and self.driver.find_element(wrong_credentials_element):
            raise InvalidLoginError("Failed login attempt detected")
        
        if timeout > 0:
            time.sleep(timeout)
            self.wait.until(EC.presence_of_element_located(check_element))

        if check_element:
            self.wait.until(EC.presence_of_element_located(check_element))

    def _setup_driver(self, url, resolution):
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