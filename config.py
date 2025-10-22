"""
Configuration for different websites
Each site config contains detailed selectors and flow for automation
"""
import os

SITES_CONFIG = {
    'freelisting': {
        'name': 'FreeListing UK',
        'domain': 'freelistinguk.com',
        'base_url': 'https://www.freelistinguk.com',
        
        'registration': {
            'url': 'https://www.freelistinguk.com/register',
            'fields': {
                'name': ['input[name="name"]', '#name'],
                'username': ['input[name="user_login"]', '#user_login'],
                'email': ['input[name="user_email"]', '#user_email'],
                'password': ['input[name="pass1"]', '#pass1'],
                'confirm_password': ['input[name="pass2"]', '#pass2'],
            },
            'submit_button': ['input[name="register"]', '#register', 'Register'],
            'wait_after_submit': 5,
            'check_already_registered': True,  # Check if email exists
        },
        
        'email_verification': {
            'required': True,
            'redirects_to_login': True,
            'wait_for_email': 120,
        },
        
        'login': {
            'url': 'https://www.freelistinguk.com/login',
            'fields': {
                'username': ['input[name="user_login"]', '#user_login'],
                'password': ['input[name="password"]', '#password'],
            },
            'submit_button': ['input[name="login"]', '#login', 'Login'],
            'wait_after_login': 3,
        },
        
        'listing': {
            'type': 'listing',
            'create_url': 'https://www.freelistinguk.com/create-listing',
            'navigation': ['Create Listing', 'create listing'],
            'fields': {
                'title': ['input[name="listing_title"]'],
                'address': ['input[name="address"]', '#listing-address'],
                'area': ['input[name="area"]', '#area'],
                'pincode': ['input[name="pincode"]', '#pincode'],
                'state': ['input[name="state"]', '#listing-state'],
                'city': ['input[name="city"]', '#listing-city'],
                'phone': ['input[name="phone"]'],
                'website': ['input[name="website"]'],
                'description': ['textarea[name="listing_content"]'],  # Correct field name
            },
            # Categories are CHECKBOXES - need special handling
            'category_checkboxes': 'input[name="listing_category[]"]',
            'category_limit': 5,  # Max 5 categories
            'checkbox_terms': ['input[name="agree_terms"]'],
            'submit_button': ['#submit', 'input[type="submit"]'],
            'wait_after_submit': 5,
        },
        
        'get_public_url': {
            'my_listings_url': 'https://www.freelistinguk.com/my-listings',
            'click_recent': True,
            'preview_button': ['Preview', 'preview', 'View'],
            'url_pattern': 'https://www.freelistinguk.com/listings/',
        },
        
        'special': {
            'has_captcha': True,
            'slow_loading': False,
        }
    },
    
    'yplocal': {
        'name': 'YP Local',
        'domain': 'yplocal.com',
        'base_url': 'https://www.yplocal.com',
        
        'registration': {
            'url': 'https://www.yplocal.com/checkout/3',
            'fields': {
                'email': ['input[name="email"]', '#email', 'input[type="email"]'],
                'confirm_email': ['input[name="confirm_email"]', 'input[name="email2"]'],
                'password': ['input[name="password"]', 'input[type="password"]'],
                'confirm_password': ['input[name="confirm_password"]', 'input[name="password2"]'],
            },
            'submit_button': ['Create My Profile', 'create my profile', 'button[type="submit"]'],
            'wait_after_submit': 5,
        },
        
        'email_verification': {
            'required': False,
        },
        
        'login': {
            'url': 'https://www.yplocal.com/login?action=loggedout',
            'fields': {
                'email': ['input[name="email"]', '#email'],
                'password': ['input[name="password"]', 'input[type="password"]'],
            },
            'submit_button': ['Login', 'button[type="submit"]'],
            'wait_after_login': 3,
        },
        
        'listing': {
            'type': 'listing',
            'create_url': None,  # Need to navigate via button
            'navigation': ['Submit News', 'submit news'],
            'fields': {
                'website': ['input[name="website"]', 'input[name="url"]'],
                'title': ['input[name="title"]', '#title'],
                'category': ['select[name="category"]', '#category'],
                'tags': ['input[name="tags"]', '#tags'],
                'location': ['select[name="location"]', '#location'],
                'email': ['input[name="email"]', 'input[type="email"]'],
                'phone': ['input[name="phone"]', 'input[type="tel"]'],
                'address': ['input[name="address"]', 'textarea[name="address"]'],
                'description': ['textarea[name="description"]', '#description'],
            },
            'category_value': 'Technology',
            'checkbox_terms': ['input[type="checkbox"]'],
            'submit_button': ['Preview and Submit', 'preview and submit', 'Submit'],
            'wait_after_submit': 5,
        },
        
        'get_public_url': {
            'my_listings_url': None,
            'navigation': ['My Business', 'my business'],
            'click_recent': True,
            'preview_button': ['Preview', 'View'],
            'url_pattern': 'yplocal.com',
        },
        
        'special': {
            'has_captcha': True,
            'slow_loading': False,
        }
    },
    
    'directorynode': {
        'name': 'Directory Node',
        'domain': 'directorynode.com',
        'base_url': 'https://directorynode.com',
        
        'registration': {
            'url': 'https://directorynode.com/register/',
            'fields': {
                'username': ['input[name="username"]', '#username'],
                'email': ['input[name="email"]', 'input[type="email"]'],
                'password': ['input[name="password"]', 'input[type="password"]'],
                'confirm_password': ['input[name="confirm_password"]', 'input[name="password2"]'],
                'nickname': ['input[name="nickname"]', '#nickname'],
            },
            'submit_button': ['Register', 'button[type="submit"]'],
            'wait_after_submit': 5,
        },
        
        'email_verification': {
            'required': False,
        },
        
        'login': {
            'url': 'https://directorynode.com/login/',
            'fields': {
                'email': ['input[name="email"]', '#email'],
                'password': ['input[name="password"]', 'input[type="password"]'],
            },
            'submit_button': ['Login', 'button[type="submit"]'],
            'wait_after_login': 3,
        },
        
        'listing': {
            'type': 'directory',
            'create_url': 'https://directorynode.com/submit-directory/',
            'navigation': ['Add Directory', 'add directory'],
            'fields': {
                'website': ['input[name="website"]', 'input[name="url"]'],
                'title': ['input[name="title"]', '#title'],
                'category': ['select[name="category"]', '#category'],
                'tags': ['input[name="tags"]', '#tags'],
                'location': ['select[name="location"]', '#location'],
                'email': ['input[name="email"]', 'input[type="email"]'],
                'phone': ['input[name="phone"]', 'input[type="tel"]'],
                'address': ['input[name="address"]', 'textarea[name="address"]'],
                'description': ['textarea[name="description"]', '#description'],
            },
            'category_value': 'Technology',
            'checkbox_terms': ['input[type="checkbox"]'],
            'submit_button': ['Preview and Submit', 'preview and submit', 'Submit'],
            'wait_after_submit': 5,
        },
        
        'get_public_url': {
            'my_listings_url': None,
            'navigation': ['My Business', 'my business'],
            'click_recent': True,
            'preview_button': ['Preview', 'View'],
            'url_pattern': 'directorynode.com',
        },
        
        'special': {
            'has_captcha': True,
            'slow_loading': False,
        }
    },
    
    'unolist': {
        'name': 'Unolist',
        'domain': 'unolist.in',
        'base_url': 'https://unolist.in',
        
        'registration': {
            'url': 'https://unolist.in/Reg/registration.html',
            'fields': {
                # EXACT selectors from unolist.txt
                'email': ['input[name="email"]', '#email'],
                'password': ['input[name="pword"]', '#pword'],
                'confirm_password': ['input[name="cpword"]', '#cpword'],
                'first_name': ['input[name="fname"]', '#fname'],
                'last_name': ['input[name="lname"]', '#lname'],
                'phone': ['input[name="phone"]', '#phone'],
            },
            'checkbox_terms': ['input[name="agriment"]'],
            'submit_button': ['input[type="image"]', 'input[src*="register.gif"]', 'input[alt="register"]', 'input[type="submit"]'],
            'wait_after_submit': 5,
        },
        
        'email_verification': {
            'required': False,
        },
        
        'login': {
            'url': 'https://unolist.in/login/login.html',
            'fields': {
                'email': ['input[name="email"]', '#email'],
                'password': ['input[name="pword"]', '#pword'],
            },
            'submit_button': ['input[name="submit"]', 'input[type="submit"]'],
            'wait_after_login': 3,
        },
        
        'listing': {
            'type': 'ad',
            'create_url': 'https://unolist.in/postfreead/',
            'navigation': ['Post Free Ad', 'post free ad'],
            'fields': {
                'choose_city': ['input[name="choose_city"]', '#choose_city'],
                'ask_area': ['input[name="ask_area"]', '#ask_area'],
                'title': ['input[name="adtitle"]', '#adtitle'],
                'website': ['input[name="url"]'],
                'email': ['input[name="email"]'],
                'email_again': ['input[name="email_again"]'],
                'phone': ['input[name="phone"]', '#phone'],
            },
            'radio_buttons': {
                'inthisad': ['input[name="inthisad"]'],
                'iama': ['input[name="iama"]'],
            },
            'checkbox_fields': {
                'othercontactok': ['input[name="othercontactok"]'],
                'agree': ['input[name="agree"]'],
            },
            'submit_button': ['input[type="submit"]', 'button[type="submit"]'],
            'wait_after_submit': 5,
        },
        
        'get_public_url': {
            'my_listings_url': 'https://unolist.in/myaccount/myclassifieds.html',
            'navigation': ['My Account', 'My Classifieds'],
            'click_recent': True,
            'url_pattern': 'unolist.in',
        },
        
        'special': {
            'has_captcha': True,
            'slow_loading': False,
        }
    },
}

# Active sites to process
TARGET_SITES = ['yplocal']

# Credentials storage file
CREDENTIALS_FILE = 'credentials.json'
CREDENTIALS_PATH = os.environ.get("CREDENTIALS_PATH", "credentials.json")

# Default values for listings
DEFAULT_LISTING_DATA = {
    'title': 'Professional Digital Services',
    'description': 'We provide comprehensive digital solutions including web development, SEO optimization, and digital marketing services. Our team specializes in creating modern, responsive websites and helping businesses establish a strong online presence. Contact us for professional digital services tailored to your business needs.',
    'phone': '+91 9999999999',  # Indian format for Unolist
    'address': '123 High Street, Westminster',
    'city': 'Mumbai',
    'area': 'Andheri',
    'category': 'Information Technology',
    'tags': 'technology, web services, digital marketing',
}