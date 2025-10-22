import random
import string
from faker import Faker

class DataGenerator:
    """Generate random user data for registrations"""
    
    def __init__(self):
        self.fake = Faker()
        
    def generate_user_data(self, email, website_url, password):
        """Generate complete user data for registration"""
        first_name = self.fake.first_name()
        last_name = self.fake.last_name()
        
        # Generate username variations
        username_base = f"{first_name.lower()}{last_name.lower()}"
        username = self._generate_unique_username(username_base)
        
        return {
            'first_name': first_name,
            'last_name': last_name,
            'full_name': f"{first_name} {last_name}",
            'username': username,
            'email': email,
            'password': password,
            'website': website_url,
            'bio': self._generate_bio(),
            'company': self.fake.company(),
            'phone': self.fake.phone_number(),
            'address': self.fake.address().replace('\n', ', '),
            'city': self.fake.city(),
            'country': self.fake.country()
        }
    
    def _generate_unique_username(self, base):
        """Create unique username with random numbers"""
        random_suffix = ''.join(random.choices(string.digits, k=4))
        variations = [
            f"{base}{random_suffix}",
            f"{base}_{random_suffix}",
            f"{base}.{random_suffix}",
            f"{base}{random.choice(string.ascii_lowercase)}{random_suffix}"
        ]
        return random.choice(variations)
    
    def _generate_bio(self):
        """Generate a simple bio"""
        templates = [
            "Digital enthusiast | Tech lover",
            "Exploring the digital world",
            "Content creator and tech geek",
            "Passionate about technology",
            "Building digital presence"
        ]
        return random.choice(templates)
    
    def generate_random_string(self, length=10):
        """Generate random alphanumeric string"""
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))