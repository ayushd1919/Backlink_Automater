import imaplib
import email
import time
import re
from email.header import decode_header
from bs4 import BeautifulSoup

class EmailHandler:
    """Handle email verification and link extraction"""
    
    def __init__(self, email_address, app_password):
        self.email_address = email_address
        self.app_password = app_password
        self.imap_server = "imap.gmail.com"
        self.imap_port = 993
        
    def connect(self):
        """Connect to Gmail IMAP server"""
        try:
            self.mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            self.mail.login(self.email_address, self.app_password)
            print(f"✓ Connected to email: {self.email_address}")
            return True
        except Exception as e:
            print(f"✗ Email connection failed: {str(e)}")
            return False
    
    def disconnect(self):
        """Disconnect from IMAP server"""
        try:
            self.mail.logout()
        except:
            pass
    
    def get_verification_link(self, domain, max_wait=120, check_interval=10):
        """
        Wait for and extract verification link from email
        
        Args:
            domain: Domain to search for (e.g., 'unolist.in')
            max_wait: Maximum time to wait in seconds
            check_interval: Time between checks in seconds
        
        Returns:
            Verification link or None
        """
        print(f"⏳ Waiting for verification email from {domain}...")
        
        start_time = time.time()
        
        while (time.time() - start_time) < max_wait:
            try:
                # Select inbox
                self.mail.select('inbox')
                
                # Search for recent emails from domain
                search_criteria = f'(FROM "{domain}" UNSEEN)'
                status, messages = self.mail.search(None, search_criteria)
                
                if status == 'OK':
                    email_ids = messages[0].split()
                    
                    # Check latest emails first
                    for email_id in reversed(email_ids[-5:]):  # Check last 5 emails
                        link = self._extract_link_from_email(email_id, domain)
                        if link:
                            print(f"✓ Found verification link!")
                            return link
                
                # Wait before next check
                print(f"   Checking again in {check_interval}s... ({int(time.time() - start_time)}s elapsed)")
                time.sleep(check_interval)
                
            except Exception as e:
                print(f"⚠ Error checking email: {str(e)}")
                time.sleep(check_interval)
        
        print(f"✗ Verification email not received within {max_wait}s")
        return None
    
    def _extract_link_from_email(self, email_id, domain):
        """Extract verification link from email body"""
        try:
            # Fetch email
            status, msg_data = self.mail.fetch(email_id, '(RFC822)')
            
            if status != 'OK':
                return None
            
            # Parse email
            email_body = msg_data[0][1]
            email_message = email.message_from_bytes(email_body)
            
            # Get email content
            body = self._get_email_body(email_message)
            
            if not body:
                return None
            
            # Extract links
            links = self._extract_links(body)
            
            # Find verification link containing domain
            for link in links:
                if domain in link and any(keyword in link.lower() for keyword in 
                    ['verify', 'confirm', 'activate', 'validation', 'token', 'validate']):
                    return link
            
            # Fallback: return any link with domain
            for link in links:
                if domain in link:
                    return link
            
            return None
            
        except Exception as e:
            print(f"⚠ Error extracting link: {str(e)}")
            return None
    
    def _get_email_body(self, email_message):
        """Extract email body from message"""
        body = ""
        
        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                
                if content_type == "text/plain" or content_type == "text/html":
                    try:
                        payload = part.get_payload(decode=True)
                        body += payload.decode('utf-8', errors='ignore')
                    except:
                        pass
        else:
            try:
                payload = email_message.get_payload(decode=True)
                body = payload.decode('utf-8', errors='ignore')
            except:
                pass
        
        return body
    
    def _extract_links(self, text):
        """Extract all URLs from text"""
        # HTML links
        soup = BeautifulSoup(text, 'html.parser')
        links = [a.get('href') for a in soup.find_all('a', href=True)]
        
        # Plain text URLs
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        text_links = re.findall(url_pattern, text)
        
        all_links = links + text_links
        
        # Clean and deduplicate
        cleaned_links = []
        for link in all_links:
            # Remove trailing punctuation and whitespace
            link = link.rstrip('.,;:!?)>]').strip()
            if link and link not in cleaned_links:
                cleaned_links.append(link)
        
        return cleaned_links