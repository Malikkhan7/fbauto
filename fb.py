import threading
from queue import Queue
import requests
import random
import string
import json
import hashlib
import time
import re

from faker import Faker

# Green text color for terminal output
GREEN = '\033[92m'
RESET = '\033[0m'

print(f"""
{GREEN}┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓           
> › Github :- @khanalex
> › By      :- AL3X KHAN
> › Proxy Support Added by @coopers-lab
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛{RESET}                """)
print(GREEN + '\x1b[38;5;208m⇼'*60 + RESET)

MAIL_API = "https://api.mail.tm"  # Mail API for temporary email

# Function to generate random string (for usernames)
def generate_random_string(length):
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for i in range(length))

# Get available email domains
def get_mail_domains():
    url = f"{MAIL_API}/domains"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['hydra:member']
    return None

# Create a new temporary email account
def create_mail_tm_account():
    fake = Faker()
    mail_domains = get_mail_domains()
    if not mail_domains:
        print(f"{GREEN}[×] Failed to fetch email domains.{RESET}")
        return None, None

    domain = random.choice(mail_domains)['domain']
    username = generate_random_string(10)
    password = fake.password()
    email = f"{username}@{domain}"

    url = f"{MAIL_API}/accounts"
    headers = {"Content-Type": "application/json"}
    data = {"address": email, "password": password}       

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        print(f"{GREEN}[✔] Email Created: {email}{RESET}")
        return email, password
    else:
        print(f"{GREEN}[×] Email Creation Failed: {response.text}{RESET}")
        return None, None

# Function to get email token for accessing inbox
def get_mail_token(email, password):
    url = f"{MAIL_API}/token"
    data = {"address": email, "password": password}
    response = requests.post(url, json=data)
    if response.status_code == 200:
        return response.json()["token"]
    return None

# Extract OTP from email
def get_otp_from_email(email, password):
    token = get_mail_token(email, password)
    if not token:
        print("[×] Failed to get email token")
        return None

    headers = {"Authorization": f"Bearer {token}"}
    inbox_url = f"{MAIL_API}/messages"

    for _ in range(10):  # Retry for 50 seconds
        response = requests.get(inbox_url, headers=headers)
        if response.status_code == 200:
            messages = response.json()["hydra:member"]
            for msg in messages:
                if "Facebook" in msg["subject"]:
                    msg_url = f"{MAIL_API}/messages/{msg['id']}"
                    msg_details = requests.get(msg_url, headers=headers).json()
                    otp_match = re.search(r"\b\d{5}\b", msg_details["text"])
                    if otp_match:
                        return otp_match.group(0)
        time.sleep(5)  # Wait before checking again

    print("[×] OTP not found in email")
    return None

# Facebook Account Registration
def register_facebook_account(email, password, first_name, last_name, birthday):
    api_key = '882a8490361da98702bf97a021ddc14d'
    secret = '62f8ce9f74b12f84c123cc23437a4a32'
    gender = random.choice(['M', 'F'])

    # Fetch OTP from email
    otp = get_otp_from_email(email, password)
    if not otp:
        print(f"{GREEN}[×] OTP not received. Cannot proceed.{RESET}")
        return

    print(f"{GREEN}[✔] OTP Received: {otp}{RESET}")

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
        'return_multiple_errors': True
    }

    sorted_req = sorted(req.items(), key=lambda x: x[0])
    sig = ''.join(f'{k}={v}' for k, v in sorted_req)
    ensig = hashlib.md5((sig + secret).encode()).hexdigest()
    req['sig'] = ensig
    api_url = 'https://b-api.facebook.com/method/user.register'
    
    response = requests.post(api_url, data=req)
    reg = response.json()

    if reg and 'new_user_id' in reg:
        user_id = reg['new_user_id']
        token = reg['session_info']['access_token']

        print(f"""{GREEN}
----------- GENERATED -----------
EMAIL    : {email}
ID       : {user_id}
PASSWORD : {password}
NAME     : {first_name} {last_name}
BIRTHDAY : {birthday} 
GENDER   : {gender}
TOKEN    : {token}
----------- GENERATED -----------{RESET}""")
    else:
        print(f'{GREEN}[×] Facebook account creation failed.{RESET}')

# Main Execution
email, password = create_mail_tm_account()
if email:
    fake = Faker()
    first_name = fake.first_name()
    last_name = fake.last_name()
    birthday = fake.date_of_birth(minimum_age=18, maximum_age=45)

    register_facebook_account(email, password, first_name, last_name, birthday)
