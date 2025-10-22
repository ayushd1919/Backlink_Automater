"""
Backlink Automator - Main Script
Automates registration, verification, login, and profile updates across multiple sites
"""

import os
import sys
import time
import json
from dotenv import load_dotenv
from datetime import datetime

# Import utilities
from utils.data_generator import DataGenerator
from utils.email_handler import EmailHandler
from utils.browser_handler import BrowserHandler
from utils.logger import BacklinkLogger
from utils.site_handler import SiteHandler
from config import TARGET_SITES, SITES_CONFIG, CREDENTIALS_FILE


class BacklinkAutomator:
    """Main automation class"""
    
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Initialize components
        self.email_address = os.getenv('EMAIL_ADDRESS')
        self.email_password = os.getenv('EMAIL_APP_PASSWORD')
        self.website_url = os.getenv('WEBSITE_URL', 'https://google.com')
        self.user_password = os.getenv('USER_PASSWORD')
        self.headless = os.getenv('HEADLESS_MODE', 'False').lower() == 'true'
        
        # Validate configuration
        if not all([self.email_address, self.email_password, self.user_password]):
            print("❌ Missing configuration in .env file!")
            print("Required: EMAIL_ADDRESS, EMAIL_APP_PASSWORD, USER_PASSWORD")
            sys.exit(1)
        
        # Initialize utilities
        self.data_gen = DataGenerator()
        self.email_handler = EmailHandler(self.email_address, self.email_password)
        self.browser = BrowserHandler(headless=self.headless)
        self.logger = BacklinkLogger()
        
        self.logger.info("Backlink Automator initialized")
        self.logger.info(f"Email: {self.email_address}")
        self.logger.info(f"Website URL: {self.website_url}")
        self.logger.info(f"Target sites: {len(TARGET_SITES)}")
    
    def process_site(self, site_key):
        """
        Process a single site: register, verify, login, create listing
        
        Args:
            site_key: Site key from SITES_CONFIG
        """
        if site_key not in SITES_CONFIG:
            self.logger.error(f"Site '{site_key}' not found in configuration")
            return
        
        site_config = SITES_CONFIG[site_key]
        site_name = site_config['name']
        domain = site_config['domain']
        
        try:
            # Generate user data
            user_data = self.data_gen.generate_user_data(
                self.email_address,
                self.website_url,
                self.user_password
            )
            
            self.logger.info(f"Generated username: {user_data['username']}")
            
            # Create site handler - FIXED: Pass correct parameters
            site_handler = SiteHandler(
                config=site_config,
                browser=self.browser,
                email_handler=self.email_handler,
                user_data=user_data,
                website_url=self.website_url,
                logger=self.logger
            )
            
            # Process the site
            result = site_handler.process()
            
            # Log result
            self.logger.log_site_result(
                site_name=site_name,
                domain=domain,
                status=result['status'],
                profile_url=result.get('profile_url'),
                error=result.get('error')
            )
            
        except Exception as e:
            self.logger.error(f"Error processing {site_name}: {str(e)}")
            self.logger.log_site_result(
                site_name=site_name,
                domain=domain,
                status='failed',
                error=str(e)
            )
    
    def run(self):
        """Run automation for all target sites"""
        self.logger.info("\n🚀 Starting Backlink Automation")
        self.logger.info(f"Processing {len(TARGET_SITES)} sites...\n")
        
        try:
            # Start browser
            self.browser.start()
            
            # Connect to email
            self.email_handler.connect()
            
            # Process each site
            for i, site_key in enumerate(TARGET_SITES, 1):
                self.logger.info(f"\n[{i}/{len(TARGET_SITES)}] Starting {site_key}...")
                
                self.process_site(site_key)
                
                # Delay between sites
                if i < len(TARGET_SITES):
                    delay = int(os.getenv('ACTION_DELAY', 5))
                    self.logger.info(f"\nWaiting {delay}s before next site...")
                    time.sleep(delay)
            
        except KeyboardInterrupt:
            self.logger.warning("\n\n⚠️ Automation interrupted by user")
        
        finally:
            # Cleanup
            self.email_handler.disconnect()
            self.browser.close()
            
            # Generate report
            self.logger.info("\n📊 Generating final report...")
            self.logger.generate_report()
            self.logger.print_summary()
            
            self.logger.info("\n✅ Automation complete!")


def main():
    """Entry point"""
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║         BACKLINK AUTOMATOR v1.0                          ║
    ║         Automated Listing Creation & Backlinking         ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    automator = BacklinkAutomator()
    automator.run()


if __name__ == "__main__":
    main()