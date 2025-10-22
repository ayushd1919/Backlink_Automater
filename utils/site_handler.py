import time
import json
import os
from datetime import datetime
from utils.credentials import get_site_credentials
from typing import Dict, List

# Import default listing data
DEFAULT_LISTING_DATA = {
    'title': 'Professional Business Services',
    'address': '123 Business Street',
    'area': 'Downtown',
    'pincode': '10001',
    'state': 'New York',
    'city': 'New York',
    'phone': '+1-555-0123',
    'description': 'We provide high-quality professional services to help your business grow. Contact us today for a consultation.',
}

CREATE_LISTING_URL = "https://www.freelistinguk.com/create-listing-form?currency=1&plan=1"
MY_LISTINGS_URL = "https://www.freelistinguk.com/my-listings"
    
        # ---------- UNOlist (unolist.in) ----------
UNO_REG_URL = "https://unolist.in/Reg/registration.html"
UNO_LOGIN_URL = "https://unolist.in/login/login.html"
UNO_POST_URL = "https://unolist.in/postfreead/"
UNO_MYCLASSIFIEDS_URL = "https://unolist.in/myaccount/myclassifieds.html"  

class SiteHandler:
    """Handles automation for a specific site"""
    
    def __init__(self, config, browser, email_handler, user_data, website_url, logger):
        self.config = config
        self.browser = browser
        self.email_handler = email_handler
        self.user_data = user_data
        self.website_url = website_url
        self.logger = logger
        self.credentials_file = 'credentials.json'

    # Add this improved method to your site_handler.py

    def _unolist_register_or_login(self) -> str:
        """Register → if email exists then Login. Uses exact selectors with enhanced image button handling."""
        # Prefer saved creds
        self.load_existing_credentials()
        email = self.user_data.get("email", "")
        password = self.user_data.get("password", "")
        fname = self.user_data.get("first_name", self.user_data.get("full_name", "Alex")).split()[0]
        lname = self.user_data.get("last_name", "Doe")
        phone = self.user_data.get("phone", "9999999999")

        # If we already have creds, try login first
        if email and password and self._unolist_login_with_creds():
            return "logged_in_existing"

        # Registration
        self.logger.info("[unolist] Attempting registration")
        self.browser.goto(UNO_REG_URL)
        self.browser.page.wait_for_load_state("domcontentloaded")
        time.sleep(2)  # Extra wait for page to be fully ready

        # --- Fill registration fields ---
        self.logger.info("[unolist] Filling registration form...")
        self.browser.fill_input(["#email", 'input[name="email"]'], email)
        time.sleep(0.5)
        self.browser.fill_input(["#pword", 'input[name="pword"]'], password)
        time.sleep(0.5)
        self.browser.fill_input(["#cpword", 'input[name="cpword"]'], password)
        time.sleep(0.5)
        self.browser.fill_input(["#fname", 'input[name="fname"]'], fname)
        time.sleep(0.5)
        self.browser.fill_input(["#lname", 'input[name="lname"]'], lname)
        time.sleep(0.5)
        self.browser.fill_input(["#phone", 'input[name="phone"]'], phone)
        time.sleep(0.5)

        # Terms checkbox with multiple attempts
        self.logger.info("[unolist] Checking terms agreement...")
        try:
            # Method 1: Direct check
            self.browser.page.check('input[name="agriment"]', timeout=3000)
        except Exception:
            try:
                # Method 2: Click
                self.browser.page.locator('input[name="agriment"]').first.click(timeout=3000)
            except Exception:
                try:
                    # Method 3: JavaScript
                    self.browser.page.evaluate('document.querySelector(\'input[name="agriment"]\').checked = true')
                except Exception as e:
                    self.logger.warning(f"[unolist] Could not tick 'agriment': {e}")

        time.sleep(1)

        # --- ENHANCED IMAGE BUTTON CLICK ---
        self.logger.info("[unolist] Attempting to click register button...")
        clicked = False
        
        # Store current URL for comparison
        url_before = self.browser.page.url
        
        # METHOD 1: Direct click on the specific image input
        try:
            self.logger.info("  [Method 1] Direct image input click")
            register_btn = self.browser.page.locator('input[type="image"][alt="register"]').first
            
            if register_btn.count() > 0:
                # Wait for button to be visible
                register_btn.wait_for(state="visible", timeout=5000)
                
                # Scroll into view
                register_btn.scroll_into_view_if_needed(timeout=3000)
                time.sleep(0.5)
                
                # Try normal click
                try:
                    register_btn.click(timeout=3000)
                    clicked = True
                    self.logger.info("  ✓ Clicked via normal click")
                except Exception as e:
                    self.logger.warning(f"  Normal click failed: {e}")
            
        except Exception as e:
            self.logger.warning(f"  [Method 1] Failed: {e}")
        
        # METHOD 2: Force click if normal didn't work
        if not clicked:
            try:
                self.logger.info("  [Method 2] Force click")
                register_btn = self.browser.page.locator('input[type="image"][alt="register"]').first
                register_btn.click(force=True, timeout=3000)
                clicked = True
                self.logger.info("  ✓ Clicked via force click")
            except Exception as e:
                self.logger.warning(f"  [Method 2] Failed: {e}")
        
        # METHOD 3: JavaScript click on image input
        if not clicked:
            try:
                self.logger.info("  [Method 3] JavaScript click on image input")
                result = self.browser.page.evaluate('''
                    () => {
                        const btn = document.querySelector('input[type="image"][alt="register"]');
                        if (btn) {
                            btn.click();
                            return 'clicked';
                        }
                        return 'not found';
                    }
                ''')
                if result == 'clicked':
                    clicked = True
                    self.logger.info("  ✓ Clicked via JavaScript")
                else:
                    self.logger.warning(f"  Button state: {result}")
            except Exception as e:
                self.logger.warning(f"  [Method 3] Failed: {e}")
        
        # METHOD 4: Submit the form directly
        if not clicked:
            try:
                self.logger.info("  [Method 4] Direct form submission")
                result = self.browser.page.evaluate('''
                    () => {
                        const btn = document.querySelector('input[type="image"][alt="register"]');
                        if (btn && btn.form) {
                            btn.form.submit();
                            return 'form submitted';
                        }
                        // Try to find any form and submit
                        const forms = document.querySelectorAll('form');
                        if (forms.length > 0) {
                            forms[0].submit();
                            return 'first form submitted';
                        }
                        return 'no form found';
                    }
                ''')
                clicked = True
                self.logger.info(f"  ✓ Form submission result: {result}")
            except Exception as e:
                self.logger.warning(f"  [Method 4] Failed: {e}")
        
        # METHOD 5: Press Enter on the last filled field
        if not clicked:
            try:
                self.logger.info("  [Method 5] Press Enter on phone field")
                self.browser.page.locator('#phone').first.focus()
                time.sleep(0.3)
                self.browser.page.keyboard.press("Enter")
                clicked = True
                self.logger.info("  ✓ Pressed Enter")
            except Exception as e:
                self.logger.warning(f"  [Method 5] Failed: {e}")
        
        if not clicked:
            self.logger.error("[unolist] All registration submit methods failed!")
            # Take a screenshot for debugging
            try:
                self.browser.page.screenshot(path="unolist_registration_failed.png")
                self.logger.info("  Screenshot saved: unolist_registration_failed.png")
            except:
                pass
            return "registration_failed"
        
        # Wait for navigation/response
        self.logger.info("[unolist] Waiting for registration response...")
        time.sleep(3)
        
        # Try to wait for URL change or page update
        try:
            self.browser.page.wait_for_load_state("networkidle", timeout=10000)
        except:
            pass
        
        time.sleep(2)
        
        # Check if URL changed
        url_after = self.browser.page.url
        if url_after != url_before:
            self.logger.info(f"[unolist] Navigation detected: {url_before} → {url_after}")
        
        # Check response
        html = (self.browser.get_page_content() or "").lower()
        
        # Duplicate email heuristics → go login
        if any(m in html for m in ("already registered", "already exists", "email exists", "email already")):
            self.logger.info("[unolist] Email exists — logging in")
            return "logged_in_existing" if self._unolist_login_with_creds() else "login_failed"
        
        # Check for success indicators
        success_indicators = ["thank", "success", "verify", "confirmation", "registered", "welcome"]
        if any(indicator in html for indicator in success_indicators):
            self.logger.info("[unolist] Registration appears successful")
        
        # Some flows may require explicit login even after registration
        self.logger.info("[unolist] Attempting post-registration login")
        if not self._unolist_login_with_creds():
            self.logger.warning("[unolist] Post-registration login failed, retrying...")
            time.sleep(3)
            if not self._unolist_login_with_creds():
                return "login_failed"
        
        # Persist credentials
        if hasattr(self, "save_credentials"):
            self.save_credentials(profile_url=None, overwrite=False)
        
        self.logger.info("[unolist] Registered new user and logged in")
        return "registered_new"


    # DEBUGGING HELPER - Add this temporary method to diagnose issues
    def debug_unolist_form(self):
        """Debug helper to inspect the registration form"""
        self.logger.info("[DEBUG] Inspecting Unolist registration form...")
        
        try:
            form_info = self.browser.page.evaluate('''
                () => {
                    const form = document.querySelector('form');
                    const imageBtn = document.querySelector('input[type="image"][alt="register"]');
                    
                    return {
                        formExists: !!form,
                        formAction: form ? form.action : null,
                        formMethod: form ? form.method : null,
                        imageButtonExists: !!imageBtn,
                        imageButtonSrc: imageBtn ? imageBtn.src : null,
                        imageButtonVisible: imageBtn ? (imageBtn.offsetParent !== null) : false,
                        imageButtonDisabled: imageBtn ? imageBtn.disabled : null,
                        allInputs: Array.from(document.querySelectorAll('input')).map(inp => ({
                            type: inp.type,
                            name: inp.name,
                            value: inp.value ? '***' : '',
                            visible: inp.offsetParent !== null
                        }))
                    };
                }
            ''')
            
            self.logger.info(f"  Form exists: {form_info['formExists']}")
            self.logger.info(f"  Form action: {form_info['formAction']}")
            self.logger.info(f"  Image button exists: {form_info['imageButtonExists']}")
            self.logger.info(f"  Image button visible: {form_info['imageButtonVisible']}")
            self.logger.info(f"  Image button disabled: {form_info['imageButtonDisabled']}")
            
            self.logger.info("  All inputs:")
            for inp in form_info['allInputs']:
                self.logger.info(f"    - {inp['type']}: {inp['name']} (visible: {inp['visible']})")
            
            return form_info
            
        except Exception as e:
            self.logger.error(f"  Debug failed: {e}")
            return None

    def _unolist_login_with_creds(self) -> bool:
        """Login with email + password using exact selectors."""
        self.load_existing_credentials()
        email = self.user_data.get("email", "")
        password = self.user_data.get("password", "")
        if not email or not password:
            self.logger.warning("[unolist] Missing email/password for login")
            return False

        self.browser.goto(UNO_LOGIN_URL)
        self.browser.page.wait_for_load_state("domcontentloaded")

        # --- Exact login selectors ---
        self.browser.fill_input(["#email", 'input[name="email"]'], email)
        self.browser.fill_input(["#pword", 'input[name="pword"]'], password)

        clicked = (
            self._safe_click_image_button(["login", "sign in"]) or
            self.browser.click_button(['input[name="submit"]','input[type="submit"]','button[type="submit"]']) or
            self._press_enter_on('#pword')
        )
        if not clicked:
            self.logger.error("[unolist] Could not trigger login submit")
        self.browser.wait_for_navigation(20000)


        self.browser.wait_for_navigation(20000)
        html = (self.browser.get_page_content() or "").lower()
        if any(x in html for x in ("logout", "my account", "my classifieds", "post free ad")):
            self.logger.info("[unolist] Logged in")
            return True

        self.logger.warning("[unolist] Login not confirmed")
        return False

    def _unolist_create_ad(self, ad: dict) -> str:
        """Post free ad → then My Classifieds → open most recent and return its URL."""
        self.logger.info("[unolist] Opening Post Free Ad form")
        self.browser.goto(UNO_POST_URL)
        self.browser.page.wait_for_load_state("domcontentloaded")

        # --- Exact post-ad selectors ---
        self.browser.fill_input(["#choose_city", 'input[name="choose_city"]'], ad.get("choose_city", "Mumbai"))
        self.browser.fill_input(["#ask_area", 'input[name="ask_area"]'], ad.get("ask_area", "Andheri"))
        self.browser.fill_input(["#adtitle", 'input[name="adtitle"]'], ad.get("adtitle", "Quality Services Available"))

        # Radios (first option by default)
        try:
            self.browser.page.locator('input[name="inthisad"]').first.check()
        except Exception:
            pass
        try:
            self.browser.page.locator('input[name="iama"]').first.check()
        except Exception:
            pass

        self.browser.fill_input(['input[name="url"]'], ad.get("url", self.website_url if hasattr(self, "website_url") else "https://example.com"))
        self.browser.fill_input(['input[name="email"]'], ad.get("email", self.user_data.get("email", "")))
        self.browser.fill_input(['input[name="email_again"]'], ad.get("email_again", self.user_data.get("email", "")))
        self.browser.fill_input(["#phone", 'input[name="phone"]'], ad.get("phone", self.user_data.get("phone", "9999999999")))

        # Optional check + agree
        try:
            self.browser.page.locator('input[name="othercontactok"]').first.check()
        except Exception:
            pass
        try:
            self.browser.page.locator('input[name="agree"]').first.check()
        except Exception:
            self.logger.warning("[unolist] Could not tick 'agree'")

        # Submit
        self.logger.info("[unolist] Submitting ad")
        if not self.browser.click_button(['input[type="submit"]', 'button[type="submit"]', 'input[name="submit"]']):
            self.logger.error("[unolist] Could not find ad submit")
            return ""

        self.browser.wait_for_navigation(20000)

        # My Account → My Classifieds → most recent ad
        try:
            if self.browser.element_exists("a:has-text('My Account')"):
                self.browser.page.locator("a:has-text('My Account')").first.click()
                self.browser.wait_for_navigation(15000)

            if self.browser.element_exists("a:has-text('My Classifieds')"):
                self.browser.page.locator("a:has-text('My Classifieds')").first.click()
                self.browser.wait_for_navigation(15000)
            else:
                self.browser.goto(UNO_MYCLASSIFIEDS_URL)
                self.browser.page.wait_for_load_state("domcontentloaded")

            link = self.browser.page.locator("a:has-text('View'), a:has-text('Preview'), .ad-title a").first
            link.wait_for(state="visible", timeout=10000)
            link.click()
            self.browser.wait_for_navigation(15000)
            return self.browser.page.url
        except Exception as e:
            self.logger.error(f"[unolist] Could not capture public ad URL: {e}")
            return ""

    def _unolist_after_auth(self) -> str:
        """Build payload from self.user_data, then create ad and return public URL."""
        ad = {
            "choose_city": self.user_data.get("city", "Mumbai"),
            "ask_area": self.user_data.get("area", "Andheri"),
            "adtitle": self.user_data.get("business_name", self.user_data.get("full_name", "Quality Services Available")),
            "url": self.user_data.get("website", self.website_url if hasattr(self, "website_url") else "https://example.com"),
            "email": self.user_data.get("email", ""),
            "email_again": self.user_data.get("email", ""),
            "phone": self.user_data.get("phone", "9999999999"),
        }
        public_url = self._unolist_create_ad(ad)
        if public_url:
            self.user_data["profile_url"] = public_url
            if hasattr(self, "save_credentials"):
                self.save_credentials(profile_url=public_url, overwrite=False)
        return public_url
    
    def _freelistinguk_post_register_or_login(self) -> str:
        """Check registration status and handle accordingly"""
        html = self.browser.get_page_content().lower()

        duplicate_markers = (
            "already registered",
            "email already exist",
            "email already exists",
            "email address is already taken",
            "account with this email",
            "duplicate email",
        )

        is_duplicate = any(m in html for m in duplicate_markers)
        if is_duplicate:
            self.logger.info("[freelistinguk] Email exists – using credentials.json to login")
            if self._freelistinguk_login_with_saved_creds():
                return "logged_in_existing"
            return "login_failed"

        self.logger.info("[freelistinguk] Registration submitted (no duplicate banner)")
        return "registered_new"

    def _freelistinguk_login_with_saved_creds(self) -> bool:
        """Log in to freelistinguk.com using credentials.json (USERNAME ONLY)"""
        creds = get_site_credentials("Freelisting UK")
        if not creds.username:
            self.logger.error("[freelistinguk] Missing username in credentials.json for 'Freelisting UK'")
            return False

        self.browser.goto("https://www.freelistinguk.com/login")
        self.browser.page.wait_for_load_state("domcontentloaded")

        # Username field
        self.browser.fill_input([
            "input[name='username']",
            "#username",
            "input#username",
            "input[placeholder*='Username']",
        ], creds.username)

        # Password field
        self.browser.fill_input([
            "input[name='password']",
            "#password",
            "input#password",
            "input[placeholder*='Password']",
        ], creds.password)

        # Submit login
        clicked = self.browser.click_button([
            "button[type='submit']",
            "button[name='login']",
            "input[type='submit']",
            ".btn-primary",
            "Login", "Log in", "Sign in",
        ])
        if not clicked:
            self.logger.error("[freelistinguk] Could not find login submit button")
            return False

        self.browser.wait_for_navigation(15000)

        # Verify login success
        html = self.browser.get_page_content().lower()
        logged_in = (
            "logout" in html or "my account" in html or
            "/account" in html or "account-profile" in html or 
            "/user/" in html or "dashboard" in html
        )

        if logged_in:
            self.logger.info("[freelistinguk] Logged in using credentials.json (username only)")
            return True

        self.logger.warning("[freelistinguk] Login attempt did not reach dashboard")
        return False
    
    def _freelistinguk_create_listing(self, listing: Dict) -> str:
        """
        Create a listing on freelistinguk.com and return the public preview URL.
        FIXED VERSION with proper field handling and validation
        """
        self.logger.info("[freelistinguk] Opening Create Listing form")
        
        # Navigate to listing form
        self.browser.goto(CREATE_LISTING_URL)
        self.browser.page.wait_for_load_state("domcontentloaded")
        time.sleep(3)

        # ===== FILL TEXT FIELDS WITH PROPER EVENT TRIGGERING =====
        
        def fill_with_events(selector, value, field_name):
            """Fill field and trigger all necessary events"""
            try:
                self.logger.info(f"[freelistinguk] Filling {field_name}")
                element = self.browser.page.locator(selector).first
                
                if element.count() > 0:
                    element.scroll_into_view_if_needed()
                    time.sleep(0.3)
                    
                    # Clear field
                    element.click()
                    self.browser.page.keyboard.press("Control+A")
                    self.browser.page.keyboard.press("Backspace")
                    time.sleep(0.2)
                    
                    # Type value slowly
                    element.type(value, delay=50)
                    time.sleep(0.3)
                    
                    # Trigger events
                    element.dispatch_event('input')
                    element.dispatch_event('change')
                    element.dispatch_event('blur')
                    
                    # Verify
                    filled = element.input_value()
                    if filled == value:
                        self.logger.info(f"  ✓ {field_name}: {value[:50]}")
                        return True
                    else:
                        self.logger.warning(f"  ✗ {field_name} verification failed")
                        return False
                else:
                    self.logger.warning(f"  ✗ {field_name} field not found")
                    return False
                    
            except Exception as e:
                self.logger.error(f"  ✗ Error filling {field_name}: {str(e)}")
                return False
        
        # Fill all required fields
        fill_with_events("input[name='listing_title']", listing.get("title", ""), "Title")
        fill_with_events("#listing-address", listing.get("address", ""), "Address")
        fill_with_events("#area", listing.get("area", ""), "Area")
        fill_with_events("#pincode", listing.get("pincode", ""), "Pincode")
        fill_with_events("#listing-state", listing.get("state", ""), "State")
        fill_with_events("#listing-city", listing.get("city", ""), "City")
        
        # Optional location hint
        if listing.get("location_hint"):
            fill_with_events("#location-input", listing["location_hint"], "Location Hint")
            time.sleep(2)

        # ===== CATEGORY SELECTION (CRITICAL) =====
        cats: List[str] = (listing.get("categories") or [])[:5]
        if cats:
            self.logger.info(f"[freelistinguk] Selecting {len(cats)} categories")
            
            for cat in cats:
                try:
                    # Wait for autocomplete to be ready
                    time.sleep(1)
                    
                    # Focus and clear the input
                    cat_input = self.browser.page.locator("#myInput").first
                    if cat_input.count() > 0:
                        cat_input.scroll_into_view_if_needed()
                        cat_input.click()
                        time.sleep(0.3)
                        
                        # Clear existing value
                        self.browser.page.keyboard.press("Control+A")
                        self.browser.page.keyboard.press("Backspace")
                        time.sleep(0.3)
                        
                        # Type category name slowly
                        cat_input.type(cat, delay=100)
                        self.logger.info(f"  Typed: {cat}")
                        time.sleep(2)  # Wait for autocomplete dropdown
                        
                        # Try to select from dropdown
                        try:
                            # Method 1: Arrow down + Enter
                            self.browser.page.keyboard.press("ArrowDown")
                            time.sleep(0.5)
                            self.browser.page.keyboard.press("Enter")
                            time.sleep(0.5)
                            self.logger.info(f"  ✓ Selected: {cat}")
                        except:
                            # Method 2: Click first suggestion
                            try:
                                suggestions = self.browser.page.locator(".ui-menu-item, .autocomplete-suggestion, [role='option']")
                                if suggestions.count() > 0:
                                    suggestions.first.click(timeout=2000)
                                    self.logger.info(f"  ✓ Clicked suggestion: {cat}")
                                else:
                                    self.logger.warning(f"  ⚠ No suggestions found for: {cat}")
                            except Exception as e:
                                self.logger.warning(f"  ⚠ Could not select: {cat} - {str(e)}")
                        
                        time.sleep(1)
                        
                except Exception as e:
                    self.logger.error(f"  ✗ Error with category {cat}: {str(e)}")
        
        # ===== CONTACT FIELDS =====
        fill_with_events("input[name='phone']", listing.get("phone", ""), "Phone")
        fill_with_events("input[name='website']", listing.get("website", ""), "Website")
        
        # ===== DESCRIPTION (TEXT AREA) =====
        try:
            self.logger.info("[freelistinguk] Filling description")
            desc_selectors = [
                "textarea[name='listing_content']",
                "textarea[name='description']",
                "#description",
                "textarea.form-control"
            ]
            
            description = listing.get("description", "")
            desc_filled = False
            
            for selector in desc_selectors:
                try:
                    desc_elem = self.browser.page.locator(selector).first
                    if desc_elem.count() > 0:
                        desc_elem.scroll_into_view_if_needed()
                        desc_elem.click()
                        time.sleep(0.3)
                        desc_elem.fill(description)
                        desc_elem.dispatch_event('input')
                        desc_elem.dispatch_event('change')
                        time.sleep(0.5)
                        
                        if desc_elem.input_value() == description:
                            self.logger.info(f"  ✓ Description filled ({len(description)} chars)")
                            desc_filled = True
                            break
                except:
                    continue
            
            if not desc_filled:
                self.logger.warning("  ⚠ Could not fill description")
                
        except Exception as e:
            self.logger.error(f"  ✗ Description error: {str(e)}")

        # ===== TERMS CHECKBOX (CRITICAL) =====
        self.logger.info("[freelistinguk] Agreeing to terms")
        time.sleep(1)
        
        try:
            terms_checkbox = self.browser.page.locator("input[name='agree_terms']").first
            
            if terms_checkbox.count() > 0:
                terms_checkbox.scroll_into_view_if_needed()
                time.sleep(0.5)
                
                # Check if already checked
                if not terms_checkbox.is_checked():
                    # Try normal check first
                    try:
                        terms_checkbox.check()
                        time.sleep(0.3)
                    except:
                        # Fallback: click the label or surrounding div
                        try:
                            # Find and click the label
                            label = self.browser.page.locator("label[for='agree_terms']").first
                            if label.count() > 0:
                                label.click()
                            else:
                                terms_checkbox.click(force=True)
                        except:
                            terms_checkbox.click(force=True)
                    
                    time.sleep(0.5)
                    
                    # Verify it's checked
                    if terms_checkbox.is_checked():
                        self.logger.info("  ✓ Terms agreed")
                    else:
                        self.logger.warning("  ⚠ Terms checkbox may not be properly checked")
                else:
                    self.logger.info("  ✓ Terms already checked")
            else:
                self.logger.warning("  ⚠ Terms checkbox not found")
                
        except Exception as e:
            self.logger.error(f"  ✗ Terms error: {str(e)}")

        # ===== PRE-SUBMISSION DIAGNOSTICS =====
        time.sleep(2)
        self.logger.info("[freelistinguk] Running pre-submit diagnostics...")
        
        try:
            validation = self.browser.page.evaluate("""
                () => {
                    const form = document.querySelector('form');
                    const submitBtn = document.querySelector('#submit');
                    
                    // Check all required fields
                    const requiredFields = Array.from(form.querySelectorAll('[required]'));
                    const emptyFields = requiredFields.filter(f => !f.value || f.value.trim() === '');
                    
                    // Check form validity
                    const validity = form.checkValidity ? form.checkValidity() : null;
                    
                    return {
                        formExists: !!form,
                        formValid: validity,
                        emptyRequired: emptyFields.map(f => f.name || f.id || 'unknown'),
                        submitExists: !!submitBtn,
                        submitDisabled: submitBtn ? submitBtn.disabled : null,
                        formAction: form ? form.action : null,
                        termsChecked: document.querySelector('input[name="agree_terms"]')?.checked || false
                    };
                }
            """)
            
            self.logger.info(f"  Form valid: {validation['formValid']}")
            self.logger.info(f"  Terms checked: {validation['termsChecked']}")
            self.logger.info(f"  Submit disabled: {validation['submitDisabled']}")
            
            if validation['emptyRequired']:
                self.logger.warning(f"  ⚠ Empty required fields: {validation['emptyRequired']}")
            else:
                self.logger.info("  ✓ All required fields filled")
                
        except Exception as e:
            self.logger.warning(f"  Diagnostics error: {str(e)}")

        # ===== FORM SUBMISSION (IMPROVED) =====
        self.logger.info("[freelistinguk] Submitting form...")
        time.sleep(1)
        
        url_before = self.browser.page.url
        submit_success = False
        
        # METHOD 1: Enable button and click with navigation wait
        try:
            self.logger.info("  [Method 1] Click with navigation wait")
            
            # First, ensure button is enabled
            self.browser.page.evaluate("""
                () => {
                    const btn = document.querySelector('#submit');
                    if (btn) {
                        btn.disabled = false;
                        btn.removeAttribute('disabled');
                    }
                }
            """)
            
            submit_btn = self.browser.page.locator("#submit").first
            if submit_btn.count() > 0:
                submit_btn.scroll_into_view_if_needed()
                time.sleep(0.5)
                
                # Click with navigation expectation
                with self.browser.page.expect_navigation(timeout=30000, wait_until="load"):
                    submit_btn.click()
                
                time.sleep(3)
                
                if self.browser.page.url != url_before:
                    self.logger.info(f"  ✓ Navigated to: {self.browser.page.url}")
                    submit_success = True
                
        except Exception as e:
            self.logger.warning(f"  ✗ Method 1 failed: {str(e)}")
        
        # METHOD 2: JavaScript form submission with proper event handling
        if not submit_success:
            try:
                self.logger.info("  [Method 2] JavaScript form submission")
                
                result = self.browser.page.evaluate("""
                    () => {
                        return new Promise((resolve) => {
                            const form = document.querySelector('form');
                            const submitBtn = document.querySelector('#submit');
                            
                            if (!form) {
                                resolve('No form found');
                                return;
                            }
                            
                            // Enable submit button
                            if (submitBtn) {
                                submitBtn.disabled = false;
                            }
                            
                            // Create and dispatch submit event
                            const submitEvent = new SubmitEvent('submit', {
                                bubbles: true,
                                cancelable: true,
                                submitter: submitBtn
                            });
                            
                            // If event is not cancelled, submit
                            if (form.dispatchEvent(submitEvent)) {
                                // Try HTMLFormElement.submit() first
                                try {
                                    form.submit();
                                    resolve('Form.submit() called');
                                } catch (e) {
                                    // If that fails, try clicking the button
                                    if (submitBtn) {
                                        submitBtn.click();
                                        resolve('Button.click() called');
                                    } else {
                                        resolve('Submit failed: ' + e.message);
                                    }
                                }
                            } else {
                                resolve('Submit event was cancelled');
                            }
                        });
                    }
                """)
                
                self.logger.info(f"  Result: {result}")
                time.sleep(5)
                
                if self.browser.page.url != url_before:
                    self.logger.info(f"  ✓ Navigated to: {self.browser.page.url}")
                    submit_success = True
                    
            except Exception as e:
                self.logger.warning(f"  ✗ Method 2 failed: {str(e)}")
        
        # METHOD 3: Check for AJAX/in-page success
        if not submit_success:
            self.logger.info("  [Method 3] Checking for AJAX success")
            time.sleep(3)
            
            page_text = self.browser.page.content().lower()
            success_indicators = ['thank you', 'success', 'submitted', 'pending review', 'listing created']
            
            if any(indicator in page_text for indicator in success_indicators):
                self.logger.info("  ✓ Found success indicator in page")
                submit_success = True

        # ===== FINAL STATUS CHECK =====
        time.sleep(2)
        
        try:
            self.browser.page.wait_for_load_state("load", timeout=15000)
            url_after = self.browser.page.url
            
            if url_after != url_before:
                self.logger.info(f"  ✓ SUCCESS: Form submitted, redirected to: {url_after}")
            elif submit_success:
                self.logger.info(f"  ✓ SUCCESS: Form submitted (AJAX/same page)")
            else:
                self.logger.error(f"  ✗ FAILED: Still on form page: {url_after}")
                
                # Check for visible errors
                try:
                    errors = self.browser.page.locator(".error, .alert-danger, .invalid-feedback, .text-danger").all()
                    for err in errors:
                        if err.is_visible():
                            self.logger.error(f"    Error message: {err.inner_text()}")
                except:
                    pass
                    
        except Exception as e:
            self.logger.warning(f"  Status check error: {str(e)}")

        # ===== GET PUBLIC URL =====
        time.sleep(3)
        self.logger.info("[freelistinguk] Navigating to My Listings")
        
        self.browser.goto(MY_LISTINGS_URL)
        self.browser.page.wait_for_load_state("domcontentloaded")
        time.sleep(3)

        # Get the listing URL
        try:
            # Try different selectors for the listing link
            preview_selectors = [
                "a:has-text('Preview')",
                "a:has-text('View')",
                "a[href*='listings/']",
                ".listing-title a",
                "h2 a"
            ]
            
            for selector in preview_selectors:
                try:
                    link = self.browser.page.locator(selector).first
                    if link.count() > 0:
                        link.wait_for(state="visible", timeout=5000)
                        link.click()
                        time.sleep(3)
                        
                        public_url = self.browser.page.url
                        self.logger.info(f"[freelistinguk] ✓ Public URL: {public_url}")
                        return public_url
                except:
                    continue
            
            self.logger.warning("[freelistinguk] Could not find listing preview link")
            return ""
            
        except Exception as e:
            self.logger.error(f"[freelistinguk] Error getting public URL: {e}")
            return ""

    def _freelistinguk_after_auth(self):
        """Execute post-authentication flow for FreeListing UK"""
        self.logger.info("[freelistinguk] Starting post-auth listing creation")
        
        # Prepare listing data from user_data with fallbacks
        listing = {
            "title": self.user_data.get("business_name") or self.user_data.get("full_name", "Professional Business Services"),
            "address": self.user_data.get("address", "221B Baker Street"),
            "area": self.user_data.get("area", "Marylebone"),
            "pincode": self.user_data.get("pincode", "NW16XE"),
            "state": self.user_data.get("state", "England"),
            "city": self.user_data.get("city", "London"),
            "location_hint": self.user_data.get("city", "London"),
            "phone": self.user_data.get("phone", "+44 20 7946 0958"),
            "website": self.user_data.get("website", self.website_url),
            "description": self.user_data.get("description", "We provide quality services and timely support. Contact us for professional business solutions tailored to your needs."),
            "categories": (self.user_data.get("categories") or ["Business Services", "Consultants"])[:5],
        }

        public_url = self._freelistinguk_create_listing(listing)
        
        if public_url:
            # Store profile URL
            self.user_data["profile_url"] = public_url
            
            # Save credentials without overwriting existing ones
            if hasattr(self, "save_credentials"):
                self.save_credentials(profile_url=public_url, overwrite=False)
        
        return public_url
    
    def load_existing_credentials(self):
        """Load credentials for this site from credentials.json"""
        try:
            if not os.path.exists(self.credentials_file):
                return None

            with open(self.credentials_file, 'r', encoding='utf-8') as f:
                all_creds = json.load(f)

            # Normalize site name for matching
            want = self.config['name']
            want_norm = want.replace(" ", "").lower()
            found = None
            
            for k, v in all_creds.items():
                if k == want or k.replace(" ", "").lower() == want_norm:
                    found = v
                    break

            if found:
                self.logger.info(f"Found existing credentials for {want}")
                self.user_data = {
                    'username': found.get('username', ''),
                    'email': found.get('email', ''),
                    'password': found.get('password', ''),
                    'profile_url': found.get('profile_url', ''),
                }
                return self.user_data

        except Exception as e:
            self.logger.warning(f"Could not load credentials: {str(e)}")

        return None
    
    def save_credentials(self, profile_url=None, overwrite=False):
        """Save credentials to credentials.json"""
        try:
            all_creds = {}
            if os.path.exists(self.credentials_file):
                with open(self.credentials_file, 'r', encoding='utf-8') as f:
                    all_creds = json.load(f)

            site_name = self.config['name']
            exists = site_name in all_creds

            if exists and not overwrite:
                self.logger.info(f"Credentials already exist for {site_name}; not overwriting.")
                return

            all_creds[site_name] = {
                'username': self.user_data.get('username', ''),
                'email': self.user_data.get('email', ''),
                'password': self.user_data.get('password', ''),
                'profile_url': profile_url or self.user_data.get('profile_url', ''),
                'created_at': datetime.now().isoformat()
            }

            with open(self.credentials_file, 'w', encoding='utf-8') as f:
                json.dump(all_creds, f, indent=2)

            self.logger.info(f"Credentials saved to {self.credentials_file}")

        except Exception as e:
            self.logger.error(f"Failed to save credentials: {str(e)}")
    
    def register(self):
        """Handle registration process"""
        self.logger.info(f"Step 1: Registration on {self.config['name']}")
        
        reg_config = self.config['registration']
        
        # Navigate to registration page
        if not self.browser.goto(reg_config['url']):
            raise Exception("Failed to load registration page")
        
        time.sleep(2)
        
        # Check for CAPTCHA
        if self.config['special']['has_captcha']:
            if self.browser.check_captcha():
                self.logger.warning("CAPTCHA detected on registration page")
                self.browser.handle_captcha_pause()
        
        # Fill registration form
        self.logger.info("Filling registration form...")
        filled_count = 0
        
        for field_name, selectors in reg_config['fields'].items():
            value = None
            
            if field_name == 'email':
                value = self.user_data['email']
            elif field_name == 'confirm_email':
                value = self.user_data['email']
            elif field_name == 'username':
                value = self.user_data['username']
            elif field_name == 'password':
                value = self.user_data['password']
            elif field_name == 'confirm_password':
                value = self.user_data['password']
            elif field_name == 'first_name':
                value = self.user_data['first_name']
            elif field_name == 'last_name':
                value = self.user_data['last_name']
            elif field_name == 'name':
                value = self.user_data['full_name']
            elif field_name == 'nickname':
                value = self.user_data['username']
            elif field_name == 'phone':
                value = DEFAULT_LISTING_DATA['phone']
            
            if value and self.browser.fill_input(selectors, value):
                self.logger.info(f"  [OK] Filled {field_name}")
                filled_count += 1
        
        if filled_count == 0:
            self.logger.warning("No fields were filled! Check selectors")
        
        # Submit registration
        self.logger.info("Submitting registration...")
        if not self.browser.click_button(reg_config['submit_button']):
            raise Exception("Failed to click submit button")
        
        time.sleep(reg_config.get('wait_after_submit', 3))
        
        # Check registration result
        page_content = self.browser.get_page_content().lower()
        
        error_keywords = ['already exists', 'already registered', 'already taken', 'already in use']
        if any(keyword in page_content for keyword in error_keywords):
            self.logger.warning("Email/username already exists. Will proceed to login.")
            return 'already_exists'
        
        self.logger.info("[OK] Registration form submitted")
        return 'success'
    
    def login(self, force_login=False):
        """Handle login process"""
        login_config = self.config.get('login')
        
        if not login_config:
            self.logger.info("No login configuration, assuming already logged in")
            return True
        
        # Load existing credentials
        existing_creds = self.load_existing_credentials()
        
        if existing_creds:
            self.logger.info(f"Using saved credentials for {self.config['name']}")
            username = existing_creds.get('username', self.user_data.get('username'))
            email = existing_creds.get('email', self.user_data.get('email'))
            password = existing_creds.get('password', self.user_data.get('password'))
        else:
            username = self.user_data.get('username')
            email = self.user_data.get('email')
            password = self.user_data.get('password')
        
        if force_login:
            self.logger.info(f"Step 2: Navigating to login page...")
            if not self.browser.goto(login_config['url']):
                raise Exception("Failed to load login page")
            time.sleep(2)
        else:
            current_url = self.browser.get_current_url()
            if 'login' not in current_url.lower():
                self.logger.info("Already logged in, skipping login step")
                return True
            
            self.logger.info(f"Step 3: Logging in to {self.config['name']}")
            
            if login_config['url'] not in current_url:
                if not self.browser.goto(login_config['url']):
                    raise Exception("Failed to load login page")
                time.sleep(2)
        
        # Fill login form
        self.logger.info("Filling login form...")
        for field_name, selectors in login_config['fields'].items():
            value = None
            
            if field_name in ['username', 'username_or_email']:
                value = username
                self.logger.info(f"Using username: {value}")
            elif field_name == 'email':
                value = email
            elif field_name == 'password':
                value = password
            
            if value and self.browser.fill_input(selectors, value):
                self.logger.info(f"  [OK] Filled {field_name}")
        
        # Submit login
        if not self.browser.click_button(login_config['submit_button']):
            raise Exception("Failed to click login button")
        
        time.sleep(login_config.get('wait_after_login', 3))
        self.logger.info("Login completed")
        return True
   
    def verify_email(self):
        """Handle email verification if required"""
        verify_config = self.config.get('email_verification', {})

        # Skip unless explicitly required
        if not verify_config.get('required'):
            self.logger.info("No email verification required")
            return True

        self.logger.info("Step 2: Email verification")
        self.logger.info(f"Waiting for verification email from {self.config['domain']}...")

        # Graceful fallback if the email handler doesn't implement this
        if not hasattr(self.email_handler, "wait_for_verification_email"):
            self.logger.warning("Email handler does not support verification polling; skipping.")
            return True  # or raise if you prefer strict behavior

        verification_link = self.email_handler.wait_for_verification_email(
            from_domain=self.config['domain'],
            max_wait=verify_config.get('wait_for_email', 120),
        )

        if not verification_link:
            raise Exception("Verification email not received")

        if not self.browser.goto(verification_link):
            raise Exception("Failed to open verification link")

        time.sleep(verify_config.get('wait_after_verify', 3))
        self.logger.info("[OK] Email verified")
        return True


    def update_profile(self):
        """Update profile with website link"""
        self.logger.info("Step 4: Updating profile with website link")
        
        profile_config = self.config.get('profile')
        if not profile_config:
            self.logger.warning("No profile configuration available")
            return None
        
        # Navigate to profile edit page
        if 'edit_url' in profile_config:
            if not self.browser.goto(profile_config['edit_url']):
                raise Exception("Failed to load profile edit page")
        elif 'navigation' in profile_config:
            for link_text in profile_config['navigation']:
                if self.browser.click_link(link_text):
                    break
        
        time.sleep(2)
        
        # Fill website field
        if 'website_field' in profile_config:
            if self.browser.fill_input(profile_config['website_field'], self.website_url):
                self.logger.info(f"  [OK] Added website: {self.website_url}")
        
        # Fill other optional fields
        if 'fields' in profile_config:
            for field_name, selectors in profile_config['fields'].items():
                value = None
                
                if field_name == 'bio':
                    value = self.user_data.get('bio')
                elif field_name == 'company':
                    value = self.user_data.get('company')
                elif field_name == 'location':
                    value = DEFAULT_LISTING_DATA.get('city')
                
                if value and self.browser.fill_input(selectors, value):
                    self.logger.info(f"  [OK] Filled {field_name}")
        
        # Save profile
        if 'save_button' in profile_config:
            if self.browser.click_button(profile_config['save_button']):
                self.logger.info("[OK] Profile saved")
        
        time.sleep(2)
        
        # Get profile URL
        profile_url = self.browser.get_current_url()
        return profile_url
    
    def create_listing(self):
        """Create a listing with website backlink (for sites other than FreeListing)"""
        self.logger.info("Step 4: Creating listing with backlink")
        
        listing_config = self.config.get('listing')
        if not listing_config:
            self.logger.warning("No listing configuration available")
            return None
        
        # Navigate to create listing page
        if 'create_url' in listing_config and listing_config['create_url']:
            if not self.browser.goto(listing_config['create_url']):
                raise Exception("Failed to load create listing page")
            time.sleep(3)
        
        # Click through navigation if needed
        if 'navigation' in listing_config:
            for button_text in listing_config['navigation']:
                if self.browser.click_button([button_text, button_text.lower()]):
                    self.logger.info(f"  [OK] Clicked: {button_text}")
                    time.sleep(2)
        
        # Fill listing form
        self.logger.info("Filling listing form...")
        filled_count = 0
        
        for field_name, selectors in listing_config.get('fields', {}).items():
            value = None
            
            if field_name == 'title':
                value = DEFAULT_LISTING_DATA['title']
            elif field_name == 'description':
                value = DEFAULT_LISTING_DATA['description']
            elif field_name == 'website':
                value = self.website_url
            elif field_name in DEFAULT_LISTING_DATA:
                value = DEFAULT_LISTING_DATA[field_name]
            
            if value and self.browser.fill_input(selectors, value):
                self.logger.info(f"  [OK] Filled {field_name}: {value if field_name != 'description' else value[:50]+'...'}")
                filled_count += 1
        
        # Handle category checkboxes
        if 'checkbox_categories' in listing_config:
            category_selectors = listing_config['checkbox_categories']
            checked_count = 0
            for selector in category_selectors[:5]:
                if self.browser.click_checkbox([selector]):
                    checked_count += 1
            if checked_count > 0:
                self.logger.info(f"  [OK] Checked {checked_count} categories")
        
        # Handle terms checkbox
        if 'checkbox_terms' in listing_config:
            if self.browser.click_checkbox(listing_config['checkbox_terms']):
                self.logger.info("  [OK] Agreed to terms")
        
        # Submit listing
        self.logger.info("Submitting listing...")
        if 'submit_button' in listing_config:
            if self.browser.click_button(listing_config['submit_button']):
                self.logger.info("[OK] Listing submitted")
                time.sleep(listing_config.get('wait_after_submit', 5))
        
        # Get listing URL
        listing_url = self.get_public_listing_url()
        return listing_url
    
    def get_public_listing_url(self):
        """Get the public URL of the created listing"""
        url_config = self.config.get('get_public_url')
        
        if not url_config:
            return self.browser.get_current_url()
        
        self.logger.info("Step 5: Getting public listing URL")
        
        # Navigate to "My Listings" page
        if 'my_listings_url' in url_config and url_config['my_listings_url']:
            if self.browser.goto(url_config['my_listings_url']):
                time.sleep(2)
        
        # Click on the most recent listing
        if url_config.get('click_recent'):
            if 'preview_button' in url_config:
                if self.browser.click_button(url_config['preview_button']):
                    time.sleep(2)
        
        # Get current URL
        public_url = self.browser.get_current_url()
        
        # Validate URL pattern if specified
        if 'url_pattern' in url_config:
            if url_config['url_pattern'] in public_url:
                self.logger.info(f"Public URL: {public_url}")
                return public_url
        
        return public_url
    
    def create_profile_or_listing(self):
        name = (self.config.get('name') or "").strip().lower()

        if name in ("unolist", "uno list"):
            self.logger.info("[unolist] Starting register/login → post ad flow")
            status = self._unolist_register_or_login()
            return self._unolist_after_auth() if status in ("registered_new", "logged_in_existing") else ""
        """Create profile or listing with website backlink"""
        # Special handling for FreeListing UK - MUST use custom flow
        site_name = self.config.get('name', '')
        if site_name in ['FreeListing UK', 'Freelisting UK', 'freelisting uk']:
            self.logger.info("[freelistinguk] Executing custom listing creation flow")
            url = self._freelistinguk_after_auth()
            return url

        # For other sites, check if they have 'listing' config
        if 'listing' in self.config:
            listing_type = self.config.get('listing', {}).get('type')
            if listing_type in ['listing', 'directory', 'ad']:
                return self.create_listing()
        
        # Fallback to profile update if profile config exists
        if 'profile' in self.config:
            return self.update_profile()
        
        # No valid config found
        self.logger.warning(f"No listing or profile configuration found for {site_name}")
        return None
    
    def process(self):
        """Main processing flow for a site"""
        try:
            self.logger.info("="*60)
            self.logger.info(f"Processing: {self.config['name']} ({self.config['domain']})")
            self.logger.info("="*60)
            
            # Step 1: Register
            registration_result = self.register()
            
            # Step 2: Handle verification/login
            if registration_result == 'already_exists':
                self.logger.info("Account exists, proceeding to login...")
                self.login(force_login=True)
            elif self.config.get('email_verification', {}).get('required'):
                self.verify_email()
                self.login()
            else:
                self.login()
            
            # Step 3: Create profile/listing
            profile_url = self.create_profile_or_listing()
            
            # Step 4: Save credentials
            self.save_credentials(profile_url)
            
            if profile_url:
                self.logger.info(f"[OK] {self.config['name']}: Profile created!")
                self.logger.info(f"Profile URL: {profile_url}")
                return {
                    'status': 'success',
                    'profile_url': profile_url,
                    'error': None
                }
            else:
                return {
                    'status': 'partial',
                    'profile_url': None,
                    'error': 'Could not retrieve profile URL'
                }
            
        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"[ERROR] {self.config['name']}: {error_msg}")
            
            return {
                'status': 'failed',
                'profile_url': None,
                'error': error_msg
            }
    def _click_image_button(self, alt_keywords: list[str]) -> bool:
        """Click an <input type='image'> whose alt/src contains any keyword."""
        page = self.browser.page
        # alt-based
        for kw in alt_keywords:
            try:
                page.locator(f'input[type="image"][alt*="{kw}" i]').first.click()
                return True
            except Exception:
                pass
        # src-based
        for kw in alt_keywords:
            try:
                page.locator(f'input[type="image"][src*="{kw}" i]').first.click()
                return True
            except Exception:
                pass
        # generic image submit (last resort)
        try:
            page.locator('input[type="image"]').first.click()
            return True
        except Exception:
            return False
    
    def _safe_click_image_button(self, alt_or_src_keywords):
        """Robustly click <input type='image'> by alt/src. Returns True on success."""
        page = self.browser.page
        selectors = []
        for kw in alt_or_src_keywords:
            selectors += [
                f'input[type="image"][alt*="{kw}" i]',
                f'input[type="image"][src*="{kw}" i]',
            ]
        selectors += ['input[type="image"]']  # last resort

        for sel in selectors:
            try:
                loc = page.locator(sel).first
                loc.wait_for(state="visible", timeout=8000)
                # 1) scroll into view
                try:
                    loc.scroll_into_view_if_needed(timeout=3000)
                except Exception:
                    pass
                # 2) normal click
                try:
                    loc.click(timeout=4000)
                    return True
                except Exception:
                    pass
                # 3) force click
                try:
                    loc.click(timeout=3000, force=True)
                    return True
                except Exception:
                    pass
                # 4) JS click
                try:
                    loc.evaluate("el => el.click()")
                    return True
                except Exception:
                    pass
                # 5) submit nearest form via JS
                try:
                    loc.evaluate("""
                        el => {
                            const f = el.form || el.closest('form');
                            if (f) f.submit();
                        }
                    """)
                    return True
                except Exception:
                    pass
            except Exception:
                continue
        return False

    def _press_enter_on(self, selector):
        """Press Enter on a field to submit the form as a last fallback."""
        try:
            self.browser.page.locator(selector).first.focus()
            self.browser.page.keyboard.press("Enter")
            return True
        except Exception:
            return False