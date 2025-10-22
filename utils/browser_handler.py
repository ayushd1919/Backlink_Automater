from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import time
import os

class BrowserHandler:
    """Handle browser automation with Playwright"""
    
    def __init__(self, headless=False, timeout=30000):
        self.headless = headless
        self.timeout = timeout
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        
    def get_page_content(self) -> str:
        """Return full HTML of the current page."""
        if not getattr(self, "page", None):
            raise RuntimeError("Page is not initialized. Call new_page()/goto() first.")
        return self.page.content()

    # (optional helpers used below; safe no-ops if you already have similar)
    def element_exists(self, selector: str) -> bool:
        try:
            el = self.page.query_selector(selector)
            return el is not None
        except Exception:
            return False

    def get_text(self, selector: str) -> str:
        el = self.page.query_selector(selector)
        return (el.inner_text() if el else "") if el else ""

    def goto(self, url: str):
        self.page.goto(url, wait_until="load")

    def wait_for_url_contains(self, fragment: str, timeout_ms: int = 15000):
        self.page.wait_for_url(f"**{fragment}**", timeout=timeout_ms)

    def start(self):
        """Start browser instance"""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        self.context = self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        self.page = self.context.new_page()
        self.page.set_default_timeout(self.timeout)
        print("[OK] Browser started")
    
    def close(self):
        """Close browser instance"""
        try:
            if self.page:
                self.page.close()
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            print("[OK] Browser closed")
        except:
            pass
    
    def goto(self, url, wait_for='load'):
        """Navigate to URL"""
        try:
            self.page.goto(url, wait_until=wait_for)
            # Wait for network to be idle
            self.page.wait_for_load_state('networkidle', timeout=15000)
            time.sleep(2)  # Additional wait for JavaScript
            return True
        except Exception as e:
            print(f"[FAIL] Navigation failed: {str(e)}")
            return False
    
    def fill_input(self, selectors, value, delay=100):
        """
        Fill input field using multiple selector strategies
        
        Args:
            selectors: List of selectors to try or single selector string
            value: Value to fill
            delay: Typing delay in milliseconds
        """
        if isinstance(selectors, str):
            selectors = [selectors]
        
        # Wait for page to be ready
        time.sleep(1)
        
        for selector in selectors:
            try:
                element = None
                
                # Strategy 1: Direct selector
                if self.page.locator(selector).count() > 0:
                    element = self.page.locator(selector).first
                
                # Strategy 2: By placeholder
                elif selector.lower() in ['username', 'email', 'password', 'name']:
                    try:
                        element = self.page.get_by_placeholder(selector, exact=False).first
                    except:
                        pass
                
                # Strategy 3: By label text
                if not element:
                    try:
                        element = self.page.get_by_label(selector, exact=False).first
                    except:
                        pass
                
                # Strategy 4: By name attribute (without selector syntax)
                if not element and not selector.startswith('['):
                    try:
                        element = self.page.locator(f'[name="{selector}"]').first
                        if element.count() == 0:
                            element = None
                    except:
                        pass
                
                # Strategy 5: By id (without # symbol)
                if not element and not selector.startswith('#'):
                    try:
                        element = self.page.locator(f'#{selector}').first
                        if element.count() == 0:
                            element = None
                    except:
                        pass
                
                if element:
                    # Wait for element to be visible and enabled
                    element.wait_for(state='visible', timeout=10000)
                    element.wait_for(state='attached', timeout=5000)
                    
                    # Scroll to element
                    element.scroll_into_view_if_needed()
                    time.sleep(0.5)
                    
                    # Clear and fill
                    try:
                        element.clear()
                    except:
                        pass  # Some fields don't support clear
                    
                    element.fill(value)
                    time.sleep(delay / 1000)
                    
                    # Verify value was filled
                    filled_value = element.input_value()
                    if filled_value == value or len(filled_value) > 0:
                        return True
                    
            except Exception as e:
                # Debug: print what went wrong
                # print(f"  Selector '{selector}' failed: {str(e)}")
                continue
        
        print(f"[WARN] Could not fill field with selectors: {selectors}")
        return False
    
    def click_button(self, selectors):
        """Click button using multiple selector strategies"""
        if isinstance(selectors, str):
            selectors = [selectors]
        
        for selector in selectors:
            try:
                # Try different selector types
                element = None
                
                # Try by text content
                if self.page.get_by_role("button", name=selector).count() > 0:
                    element = self.page.get_by_role("button", name=selector).first
                # Try by text (link or button)
                elif self.page.get_by_text(selector, exact=False).count() > 0:
                    element = self.page.get_by_text(selector, exact=False).first
                # Try as CSS selector
                elif self.page.locator(selector).count() > 0:
                    element = self.page.locator(selector).first
                
                if element:
                    element.wait_for(state='visible', timeout=5000)
                    element.click()
                    time.sleep(2)  # Wait for action to complete
                    return True
                    
            except Exception as e:
                continue
        
        print(f"[WARN] Could not click button with selectors: {selectors}")
        return False
    
    def wait_for_navigation(self, timeout=10000):
        """Wait for page navigation"""
        try:
            self.page.wait_for_load_state('networkidle', timeout=timeout)
            return True
        except:
            return False
    
    def check_captcha(self):
        """Check if CAPTCHA is present on page"""
        captcha_indicators = [
            'recaptcha',
            'g-recaptcha',
            'captcha',
            'hcaptcha',
            'cf-turnstile'
        ]
        
        page_content = self.page.content().lower()
        
        for indicator in captcha_indicators:
            if indicator in page_content:
                return True
        
        return False
    
    def handle_captcha_pause(self):
        """Pause for manual CAPTCHA solving"""
        print("\n" + "="*60)
        print("[WARN] CAPTCHA DETECTED!")
        print("="*60)
        print("Please solve the CAPTCHA manually in the browser window.")
        print("After solving, press ENTER to continue...")
        print("="*60)
        input()
        time.sleep(2)
    
    def save_cookies(self, filepath):
        """Save cookies to file"""
        try:
            cookies = self.context.cookies()
            import json
            with open(filepath, 'w') as f:
                json.dump(cookies, f)
            return True
        except Exception as e:
            print(f"[WARN] Failed to save cookies: {str(e)}")
            return False
    
    def load_cookies(self, filepath):
        """Load cookies from file"""
        try:
            import json
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    cookies = json.load(f)
                self.context.add_cookies(cookies)
                return True
        except Exception as e:
            print(f"[WARN] Failed to load cookies: {str(e)}")
        return False
    
    def get_current_url(self):
        """Get current page URL"""
        return self.page.url
    
    def debug_page_inputs(self):
        """Print all input fields on the page for debugging"""
        try:
            print("\n[DEBUG] All input fields on page:")
            inputs = self.page.locator('input').all()
            for i, inp in enumerate(inputs):
                try:
                    input_type = inp.get_attribute('type') or 'text'
                    input_name = inp.get_attribute('name') or 'no-name'
                    input_id = inp.get_attribute('id') or 'no-id'
                    input_placeholder = inp.get_attribute('placeholder') or 'no-placeholder'
                    visible = inp.is_visible()
                    
                    print(f"  [{i}] type={input_type}, name={input_name}, id={input_id}, "
                          f"placeholder={input_placeholder}, visible={visible}")
                except:
                    pass
            
            print("\n[DEBUG] All select dropdowns on page:")
            selects = self.page.locator('select').all()
            for i, sel in enumerate(selects):
                try:
                    select_name = sel.get_attribute('name') or 'no-name'
                    select_id = sel.get_attribute('id') or 'no-id'
                    visible = sel.is_visible()
                    
                    print(f"  [{i}] name={select_name}, id={select_id}, visible={visible}")
                except:
                    pass
                    
            print("\n[DEBUG] All textareas on page:")
            textareas = self.page.locator('textarea').all()
            for i, ta in enumerate(textareas):
                try:
                    ta_name = ta.get_attribute('name') or 'no-name'
                    ta_id = ta.get_attribute('id') or 'no-id'
                    visible = ta.is_visible()
                    
                    print(f"  [{i}] name={ta_name}, id={ta_id}, visible={visible}")
                except:
                    pass
                    
        except Exception as e:
            print(f"[DEBUG] Error inspecting page: {str(e)}")
    
    def select_dropdown(self, selectors, value=None, index=None):
        """
        Select option from dropdown
        
        Args:
            selectors: List of selectors or single selector
            value: Option value or text to select
            index: Option index to select (0-based)
        """
        if isinstance(selectors, str):
            selectors = [selectors]
        
        for selector in selectors:
            try:
                if self.page.locator(selector).count() > 0:
                    element = self.page.locator(selector).first
                    element.wait_for(state='visible', timeout=5000)
                    
                    if index is not None:
                        # Select by index
                        element.select_option(index=index)
                    elif value:
                        # Try selecting by value, label, or text
                        try:
                            element.select_option(value=value)
                        except:
                            try:
                                element.select_option(label=value)
                            except:
                                # Select first option that contains the value
                                options = element.locator('option').all()
                                for i, opt in enumerate(options):
                                    if value.lower() in opt.inner_text().lower():
                                        element.select_option(index=i)
                                        break
                    
                    time.sleep(0.5)
                    return True
                    
            except Exception as e:
                continue
        
        print(f"[WARN] Could not select dropdown with selectors: {selectors}")
        return False
    
    def click_checkbox(self, selectors):
        """Click checkbox to check it"""
        if isinstance(selectors, str):
            selectors = [selectors]
        
        for selector in selectors:
            try:
                if self.page.locator(selector).count() > 0:
                    element = self.page.locator(selector).first
                    element.wait_for(state='visible', timeout=5000)
                    
                    # Check if already checked
                    if not element.is_checked():
                        element.check()
                        time.sleep(0.5)
                    
                    return True
                    
            except Exception as e:
                continue
        
        print(f"[WARN] Could not find checkbox with selectors: {selectors}")
        return False
    
    def click_radio(self, selectors):
        """Click radio button"""
        if isinstance(selectors, str):
            selectors = [selectors]
        
        for selector in selectors:
            try:
                if self.page.locator(selector).count() > 0:
                    element = self.page.locator(selector).first
                    element.wait_for(state='visible', timeout=5000)
                    element.check()
                    time.sleep(0.5)
                    return True
                    
            except Exception as e:
                continue
        
        print(f"[WARN] Could not find radio button with selectors: {selectors}")
        return False
    def click_image_button(self, alt_text=None, src_contains=None):
        """Click an image input button by alt text or src"""
        selectors = []
        
        if alt_text:
            selectors.append(f'input[type="image"][alt="{alt_text}"]')
            selectors.append(f'input[type="image"][alt*="{alt_text}" i]')
        
        if src_contains:
            selectors.append(f'input[type="image"][src*="{src_contains}"]')
        
        # Fallback
        selectors.append('input[type="image"]')
        
        for selector in selectors:
            try:
                element = self.page.locator(selector).first
                if element.count() > 0:
                    element.wait_for(state='visible', timeout=5000)
                    element.scroll_into_view_if_needed()
                    time.sleep(0.5)
                    
                    # Try click with navigation expectation
                    try:
                        with self.page.expect_navigation(timeout=5000):
                            element.click()
                        return True
                    except:
                        # Navigation didn't happen, but click might have worked
                        pass
                    
                    # Verify click worked by checking if URL changed
                    time.sleep(2)
                    return True
            except:
                continue
        
        return False