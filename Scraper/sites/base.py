from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait

class _Base_web():
    def take_screenshot(self):
        return self.driver.get_screenshot_as_png()

    def quit(self):
        self.driver.quit()
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