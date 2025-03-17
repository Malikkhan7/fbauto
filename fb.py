import threading
from queue import Queue
import requests
import random
import string
import json
import hashlib
import time
from faker import Faker

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

def generate_random_string(length):
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for i in range(length))

def get_mail_domains(proxy=None):
    url = "https://api.mail.tm/domains"
    try:
        response = requests.get(url, proxies=proxy, timeout=10)
        if response.status_code == 200:
            return response.json().get('hydra:member', [])
    except Exception as e:
        print(f'{GREEN}[×] Mail.tm Error: {e}{RESET}')
    return None

def create_mail_tm_account(proxy=None):
    fake = Faker()
    mail_domains = get_mail_domains(proxy)
    if mail_domains:
        domain = random.choice(mail_domains)['domain']
        username = generate_random_string(10)
        password = fake.password(length=12, special_chars=True, digits=True, upper_case=True, lower_case=True)
        url = "https://api.mail.tm/accounts"
        headers = {"Content-Type": "application/json"}
        data = {"address": f"{username}@{domain}", "password": password}       

        try:
            response = requests.post(url, headers=headers, json=data, proxies=proxy, timeout=10)
            if response.status_code == 201:
                print(f"{GREEN}[✓] Email Created: {username}@{domain}{RESET}")
                return f"{username}@{domain}", password
        except Exception as e:
            print(f'{GREEN}[×] Email Creation Error: {e}{RESET}')
    return None, None

def fetch_otp(email, password, proxy=None):
    token_url = "https://api.mail.tm/token"
    messages_url = "https://api.mail.tm/messages"

    try:
        response = requests.post(token_url, json={"address": email, "password": password}, proxies=proxy, timeout=10)
        if response.status_code == 200:
            token = response.json().get('token')
            headers = {"Authorization": f"Bearer {token}"}
            
            for _ in range(10):
                time.sleep(5)  # Wait for OTP to arrive
                messages = requests.get(messages_url, headers=headers, proxies=proxy).json()
                if messages and 'hydra:member' in messages:
                    for msg in messages['hydra:member']:
                        if "OTP" in msg.get('subject', ''):
                            return msg['intro']  # Extract OTP
            print(f"{GREEN}[×] OTP Not Found!{RESET}")
    except Exception as e:
        print(f'{GREEN}[×] OTP Fetching Error: {e}{RESET}')
    return None

def register_facebook_account(email, password, otp, proxy=None):
    fake = Faker()
    first_name = fake.first_name()
    last_name = fake.last_name()
    birthday = fake.date_of_birth(minimum_age=18, maximum_age=45).strftime('%Y-%m-%d')
    gender = random.choice(['M', 'F'])

    api_key = '882a8490361da98702bf97a021ddc14d'
    secret = '62f8ce9f74b12f84c123cc23437a4a32'

    if otp:
        print(f"{GREEN}[✓] OTP Received: {otp}{RESET}")  

    req = {
        'api_key': api_key,
        'attempt_login': True,
        'birthday': birthday,
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
    req['sig'] = hashlib.md5((sig + secret).encode()).hexdigest()
    
    api_url = 'https://b-api.facebook.com/method/user.register'
    response = requests.post(api_url, data=req, proxies=proxy, timeout=10)
    
    try:
        reg = response.json()
        if 'new_user_id' in reg:
            print(f"""{GREEN}
----------- ACCOUNT CREATED -----------
EMAIL    : {email}
ID       : {reg['new_user_id']}
PASSWORD : {password}
NAME     : {first_name} {last_name}
BIRTHDAY : {birthday} 
GENDER   : {gender}
OTP      : {otp} (Only for Verification)
TOKEN    : {reg['session_info']['access_token']}
----------------------------------------{RESET}""")
        else:
            print(f'{GREEN}[×] Facebook Registration Failed!{RESET}')
    except Exception as e:
        print(f'{GREEN}[×] Registration Error: {e}{RESET}')

def load_proxies():
    try:
        with open('proxies.txt', 'r') as file:
            proxies = [line.strip() for line in file]
        return [{'http': f'http://{proxy}'} for proxy in proxies]
    except:
        print(f"{GREEN}[×] proxies.txt file not found!{RESET}")
        return []

def test_proxy(proxy, q, valid_proxies):
    try:
        response = requests.get('https://api.mail.tm', proxies=proxy, timeout=5)
        if response.status_code == 200:
            valid_proxies.append(proxy)
    except:
        pass
    q.task_done()

def get_working_proxies():
    proxies = load_proxies()
    valid_proxies = []
    q = Queue()

    for proxy in proxies:
        q.put(proxy)
    
    for _ in range(10):
        worker = threading.Thread(target=worker_test_proxy, args=(q, valid_proxies))
        worker.daemon = True
        worker.start()
    
    q.join()
    return valid_proxies

def worker_test_proxy(q, valid_proxies):
    while not q.empty():
        proxy = q.get()
        test_proxy(proxy, q, valid_proxies)

working_proxies = get_working_proxies()

if not working_proxies:
    print(f'{GREEN}[×] No working proxies found. Please check your proxies.{RESET}')
else:
    num_accounts = int(input(f'{GREEN}[+] How Many Accounts You Want:  {RESET}'))
    for _ in range(num_accounts):
        proxy = random.choice(working_proxies)
        email, password = create_mail_tm_account(proxy)
        if email:
            otp = fetch_otp(email, password, proxy)
            if otp:
                register_facebook_account(email, password, otp, proxy)

print(GREEN + '\x1b[38;5;208m⇼'*60 + RESET)
