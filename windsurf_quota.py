import os
import time
import shutil
import sqlite3
from datetime import datetime
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv


class WindsurfQuotaChecker:
    def __init__(self):
        load_dotenv()
        self.email = os.getenv('WINDSURF_EMAIL')
        self.password = os.getenv('WINDSURF_PASSWORD')
        self.driver = None
        self.profile_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chrome_profile')
        
        if not self.email or not self.password:
            raise ValueError("Please set WINDSURF_EMAIL and WINDSURF_PASSWORD in .env file")
    
    def _clean_profile_lock(self):
        lock_file = os.path.join(self.profile_dir, 'SingletonLock')
        lock_file2 = os.path.join(self.profile_dir, 'SingletonCookie')
        lock_file3 = os.path.join(self.profile_dir, 'SingletonSocket')
        for f in [lock_file, lock_file2, lock_file3]:
            try:
                if os.path.exists(f):
                    os.remove(f)
            except:
                pass
    
    def setup_driver(self, headless=False):
        self._clean_profile_lock()
        
        options = uc.ChromeOptions()
        if headless:
            options.add_argument('--headless=new')
        
        options.add_argument(f'--user-data-dir={self.profile_dir}')
        
        self.driver = uc.Chrome(options=options, version_main=146, use_subprocess=True)
        time.sleep(2)
    
    def is_logged_in(self):
        self.driver.get('https://windsurf.com/subscription/usage')
        time.sleep(4)
        current_url = self.driver.current_url
        if 'login' in current_url.lower():
            print("Not logged in - redirected to login page")
            return False
        
        page_text = self.driver.find_element(By.TAG_NAME, 'body').text.lower()
        if 'quota' in page_text or 'usage' in page_text or 'remaining' in page_text:
            print("Already logged in!")
            return True
        return False
    
    def login(self):
        print("Navigating to login page...")
        self.driver.get('https://windsurf.com/account/login')
        
        wait = WebDriverWait(self.driver, 20)
        
        print("Waiting for email input field...")
        email_input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="email"], input[name="email"], input[placeholder*="email" i]'))
        )
        email_input.clear()
        email_input.send_keys(self.email)
        print(f"Entered email: {self.email}")
        
        time.sleep(1)
        
        print("Looking for password input field...")
        password_input = self.driver.find_element(By.CSS_SELECTOR, 'input[type="password"], input[name="password"]')
        password_input.clear()
        password_input.send_keys(self.password)
        print("Entered password")
        
        time.sleep(1)
        
        print("Looking for login button...")
        button_selectors = [
            (By.CSS_SELECTOR, 'button[type="submit"]'),
            (By.XPATH, '//button[contains(text(), "Log in") or contains(text(), "Sign in") or contains(text(), "Continue")]'),
            (By.XPATH, '//button[@type="submit"]'),
            (By.CSS_SELECTOR, 'button'),
        ]
        
        login_button = None
        for by, selector in button_selectors:
            try:
                login_button = self.driver.find_element(by, selector)
                break
            except:
                continue
        
        if not login_button:
            raise Exception("Could not find login button")
        
        login_button.click()
        print("Clicked login button")
        
        time.sleep(5)
        print("Login successful!")
    
    def get_quota_info(self):
        print("\nNavigating to usage page...")
        self.driver.get('https://windsurf.com/subscription/usage')
        time.sleep(4)
        
        quota_data = {
            'daily_quota': None,
            'weekly_quota': None,
            'extra_balance': None
        }
        
        print("Extracting quota information...")
        
        all_text = self.driver.find_element(By.TAG_NAME, 'body').text
        lines = all_text.split('\n')
        
        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            if 'daily quota' in line_lower:
                for j in range(i + 1, min(i + 3, len(lines))):
                    if '%' in lines[j] and 'remaining' in lines[j].lower():
                        quota_data['daily_quota'] = lines[j].strip()
                        break
            elif 'weekly quota' in line_lower:
                for j in range(i + 1, min(i + 3, len(lines))):
                    if '%' in lines[j] and 'remaining' in lines[j].lower():
                        quota_data['weekly_quota'] = lines[j].strip()
                        break
            elif 'extra usage balance' in line_lower:
                for j in range(i + 1, min(i + 3, len(lines))):
                    if '$' in lines[j]:
                        quota_data['extra_balance'] = lines[j].strip()
                        break
        
        if not any(quota_data.values()):
            daily_patterns = [
                (By.XPATH, "//*[contains(text(), 'Your daily quota')]/following::*[contains(text(), '%')]"),
                (By.XPATH, "//*[contains(text(), 'Daily')]/following::*[contains(text(), '%')]")
            ]
            weekly_patterns = [
                (By.XPATH, "//*[contains(text(), 'Your weekly quota')]/following::*[contains(text(), '%')]"),
                (By.XPATH, "//*[contains(text(), 'Weekly')]/following::*[contains(text(), '%')]")
            ]
            balance_patterns = [
                (By.XPATH, "//*[contains(text(), 'Extra usage balance')]/following::*[contains(text(), '$')]"),
                (By.XPATH, "//*[contains(text(), 'Extra')]/following::*[contains(text(), '$')]")
            ]
            
            for by, pattern in daily_patterns:
                try:
                    quota_data['daily_quota'] = self.driver.find_element(by, pattern).text.strip()
                    break
                except:
                    continue
            for by, pattern in weekly_patterns:
                try:
                    quota_data['weekly_quota'] = self.driver.find_element(by, pattern).text.strip()
                    break
                except:
                    continue
            for by, pattern in balance_patterns:
                try:
                    quota_data['extra_balance'] = self.driver.find_element(by, pattern).text.strip()
                    break
                except:
                    continue
        
        if quota_data['daily_quota']:
            print(f"Daily quota: {quota_data['daily_quota']}")
        if quota_data['weekly_quota']:
            print(f"Weekly quota: {quota_data['weekly_quota']}")
        if quota_data['extra_balance']:
            print(f"Extra balance: {quota_data['extra_balance']}")
        
        return quota_data
    
    def init_db(self):
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'windsurf_quota.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quota_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                daily_quota TEXT,
                weekly_quota TEXT,
                extra_balance TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS credit_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fetched_at TEXT NOT NULL,
                description TEXT,
                amount TEXT,
                date TEXT
            )
        ''')
        conn.commit()
        return conn
    
    def save_to_db(self, quota_data):
        conn = self.init_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO quota_history (timestamp, daily_quota, weekly_quota, extra_balance)
            VALUES (?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            quota_data.get('daily_quota'),
            quota_data.get('weekly_quota'),
            quota_data.get('extra_balance')
        ))
        conn.commit()
        print(f"Data saved to database (row id: {cursor.lastrowid})")
        conn.close()
        
        import json
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'quota_latest.json')
        with open(json_path, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'daily_quota': quota_data.get('daily_quota'),
                'weekly_quota': quota_data.get('weekly_quota'),
                'extra_balance': quota_data.get('extra_balance')
            }, f)
    
    def get_credit_history(self):
        print("\nNavigating to credit history page...")
        self.driver.get('https://windsurf.com/subscription/credit-history')
        time.sleep(4)
        
        credit_entries = []
        
        print("Extracting credit history...")
        all_text = self.driver.find_element(By.TAG_NAME, 'body').text
        lines = [line.strip() for line in all_text.split('\n') if line.strip()]
        
        i = 0
        while i < len(lines):
            line_lower = lines[i].lower()
            if 'extra usage' in line_lower and ('refill' in line_lower or 'purchase' in line_lower) and 'history of' not in line_lower:
                description = lines[i]
                amount = None
                date = None
                
                for j in range(i + 1, min(i + 5, len(lines))):
                    if '$' in lines[j] and 'extra usage' in lines[j].lower():
                        amount = lines[j].strip()
                    elif any(month in lines[j] for month in [
                        'January', 'February', 'March', 'April', 'May', 'June',
                        'July', 'August', 'September', 'October', 'November', 'December'
                    ]):
                        date = lines[j].strip()
                
                if amount or date:
                    entry = {
                        'description': description,
                        'amount': amount,
                        'date': date
                    }
                    credit_entries.append(entry)
                    print(f"  {description} | {amount} | {date}")
            i += 1
        
        if not credit_entries:
            print("No credit history entries found")
        
        return credit_entries
    
    def save_credit_history_to_db(self, credit_entries):
        if not credit_entries:
            return
        conn = self.init_db()
        cursor = conn.cursor()
        
        cursor.execute('SELECT description, amount, date, COUNT(*) as cnt FROM credit_history GROUP BY description, amount, date')
        db_counts = {}
        for row in cursor.fetchall():
            key = (row[0], row[1], row[2])
            db_counts[key] = row[3]
        
        scraped_counts = {}
        for entry in credit_entries:
            key = (entry.get('description'), entry.get('amount'), entry.get('date'))
            scraped_counts[key] = scraped_counts.get(key, 0) + 1
        
        fetched_at = datetime.now().isoformat()
        new_count = 0
        for key, scraped_n in scraped_counts.items():
            existing_n = db_counts.get(key, 0)
            to_insert = scraped_n - existing_n
            for _ in range(to_insert):
                cursor.execute('''
                    INSERT INTO credit_history (fetched_at, description, amount, date)
                    VALUES (?, ?, ?, ?)
                ''', (fetched_at, key[0], key[1], key[2]))
                new_count += 1
        
        conn.commit()
        print(f"Credit history: {new_count} new entries saved, {len(credit_entries) - new_count} already existed")
        conn.close()
    
    def close(self):
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
    
    def run(self, headless=False):
        try:
            self.setup_driver(headless=headless)
            
            print("Checking if already logged in...")
            if self.is_logged_in():
                print("Session still active - skipping login!")
            else:
                print("Need to log in...")
                self.login()
            
            quota_info = self.get_quota_info()
            self.save_to_db(quota_info)
            
            credit_entries = self.get_credit_history()
            self.save_credit_history_to_db(credit_entries)
            
            print("\n" + "="*50)
            print("WINDSURF QUOTA INFORMATION")
            print("="*50)
            print(f"Your daily quota: {quota_info['daily_quota'] or 'Not found'}")
            print(f"Your weekly quota: {quota_info['weekly_quota'] or 'Not found'}")
            print(f"Extra usage balance available: {quota_info['extra_balance'] or 'Not found'}")
            print(f"Credit history entries: {len(credit_entries)}")
            print("="*50)
            
            return quota_info
            
        except Exception as e:
            print(f"\nError occurred: {str(e)}")
            try:
                if self.driver:
                    self.driver.save_screenshot('error_screenshot.png')
                    print("Screenshot saved as error_screenshot.png")
            except:
                print("Could not save screenshot (browser may have closed)")
            raise
        finally:
            self.close()


if __name__ == "__main__":
    checker = WindsurfQuotaChecker()
    checker.run(headless=True)
