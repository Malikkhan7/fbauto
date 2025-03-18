import threading
from queue import Queue
import requests
import random
import string
import json
import hashlib
from faker import Faker
import time

# Green text color for terminal output
GREEN = '\033[92m'
RESET = '\033[0m'

print(f"""
{GREEN}┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓           
> › Github :- @khanalex
> › By      :- AL3X KHAN
> › Proxy Support Added by @coopers-lab
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛{RESET}                
""")
print(GREEN + '\x1b[38;5;208m⇼'*60 + RESET)

# Generate random string (Username)
def generate_random_string(length):
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for i in range(length))

# Getting mail domains
def get_mail_domains(proxy=None):
    url = "https://api.mail.tm/domains"
    try:
        response = requests.get(url, proxies=proxy)
        if response.status_code == 200:
            return response.json()['hydra:member']
        else:
            print(f'{GREEN}[×] E-mail Error : {response.text}{RESET}')
            return None
    except Exception as e:
        print(f'{GREEN}[×] Error : {e}{RESET}')
        return None

# Create mail.tm account
def create_mail_tm_account(proxy=None):
    fake = Faker()
    mail_domains = get_mail_domains(proxy)
    if mail_domains:
        domain = random.choice(mail_domains)['domain']
        username = generate_random_string(10)
        password = fake.password()
        birthday = fake.date_of_birth(minimum_age=18, maximum_age=45)
        first_name = fake.first_name()
        last_name = fake.last_name()

        url = "https://api.mail.tm/accounts"
        headers = {"Content-Type": "application/json"}
        data = {"address": f"{username}@{domain}", "password": password}
        
        try:
            response = requests.post(url, headers=headers, json=data, proxies=proxy)
            if response.status_code == 201:
                return f"{username}@{domain}", password, first_name, last_name, birthday
            else:
                print(f'{GREEN}[×] Email Error : {response.text}{RESET}')
                return None, None, None, None, None
        except Exception as e:
            print(f'{GREEN}[×] Error : {e}{RESET}')
            return None, None, None, None, None

# Get OTP from email inbox
def get_facebook_otp(email, password, proxy=None):
    url = "https://api.mail.tm/token"
    data = {"address": email, "password": password}
    
    try:
        response = requests.post(url, json=data, proxies=proxy)
        if response.status_code == 200:
            token = response.json()['token']
            inbox_url = "https://api.mail.tm/messages"
            headers = {"Authorization": f"Bearer {token}"}

            print(f"{GREEN}[+] Checking for OTP in email...{RESET}")
            for _ in range(10):  # Retry for 50 seconds
                inbox_response = requests.get(inbox_url, headers=headers, proxies=proxy)
                if inbox_response.status_code == 200:
                    messages = inbox_response.json()['hydra:member']
                    for msg in messages:
                        if "Facebook" in msg["from"]["address"]:  # Check if mail is from Facebook
                            otp = ''.join(filter(str.isdigit, msg["subject"]))  # Extract numbers (OTP)
                            print(f"{GREEN}[+] OTP Received: {otp}{RESET}")
                            return otp
                time.sleep(5)  # Wait and retry
            
            print(f'{GREEN}[×] OTP not received in time.{RESET}')
            return None
        else:
            print(f'{GREEN}[×] Error getting email token: {response.text}{RESET}')
            return None
    except Exception as e:
        print(f'{GREEN}[×] Error : {e}{RESET}')
        return None

# Facebook account registration with OTP
def register_facebook_account(email, password, first_name, last_name, birthday, proxy=None):
    api_key = '882a8490361da98702bf97a021ddc14d'
    secret = '62f8ce9f74b12f84c123cc23437a4a32'
    gender = random.choice(['M', 'F'])

    # Get OTP from email
    otp = get_facebook_otp(email, password, proxy)
    if not otp:
        print(f"{GREEN}[×] OTP not received. Skipping account.{RESET}")
        return

    req = {
        'api_key': api_key,
        'attempt_login': True,
        'birthday': birthday.strftime('%Y-%m-%d'),
        'client_country_code': 'EN',
        'fb_api_caller_class': 'com.facebook.registration.protocol.RegisterAccountMethod',
        'fb_api_req_friendly_name': 'registerAccount',
        'firstname': first_name,
        'format': 'json',
        'gender': gender,
        'lastname': last_name,
        'email': email,
        'locale': 'en_US',
        'method': 'user.register',
        'password': password,
        'reg_instance': generate_random_string(32),
        'return_multiple_errors': True,
        'otp': otp  # OTP added for verification
    }
    
    sorted_req = sorted(req.items(), key=lambda x: x[0])
    sig = ''.join(f'{k}={v}' for k, v in sorted_req)
    ensig = hashlib.md5((sig + secret).encode()).hexdigest()
    req['sig'] = ensig
    api_url = 'https://b-api.facebook.com/method/user.register'
    reg = _call(api_url, req, proxy)
    
    if reg and 'new_user_id' in reg:
        id = reg['new_user_id']
        token = reg['session_info']['access_token']
        
        print(f"""{GREEN}
-----------GENERATED-----------
EMAIL : {email}
ID : {id}
PASSWORD : {password}
NAME : {first_name} {last_name}
BIRTHDAY : {birthday} 
GENDER : {gender}
-----------GENERATED-----------
Token : {token}
-----------GENERATED-----------{RESET}""")
    else:
        print(f'{GREEN}[×] Failed to generate Facebook account.{RESET}')

# Helper function for API call
def _call(url, params, proxy=None, post=True):
    headers = {'User-Agent': '[FBAN/FB4A;FBAV/35.0.0.48.273;FBDM/{density=1.33125,width=800,height=1205};FBLC/en_US;FBCR/;FBPN/com.facebook.katana;FBDV/Nexus 7;FBSV/4.1.1;FBBK/0;]'}
    if post:
        response = requests.post(url, data=params, headers=headers, proxies=proxy)
    else:
        response = requests.get(url, params=params, headers=headers, proxies=proxy)
    return response.json()

# Load proxies
def load_proxies():
    with open('proxies.txt', 'r') as file:
        proxies = [line.strip() for line in file]
    return [{'http': f'http://{proxy}'} for proxy in proxies]

# Main Execution
proxies = load_proxies()
for i in range(int(input(f'{GREEN}[+] How Many Accounts You Want:  {RESET}'))):
    proxy = random.choice(proxies) if proxies else None
    email, password, first_name, last_name, birthday = create_mail_tm_account(proxy)
    if email:
        register_facebook_account(email, password, first_name, last_name, birthday, proxy)

print(GREEN + '\x1b[38;5;208m⇼'*60 + RESET)
