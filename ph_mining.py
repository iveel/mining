import pandas as pd
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pickle
import time
from tqdm import *
import urllib
import codecs
import warnings
import platform
import bs4 as bs
import json
import numpy as np
import MySQLdb

warnings.filterwarnings('ignore')


class sql:

    dsn = ("sql8.freemysqlhosting.net","sql8177810","4MeU7jpiBz","sql8177810")

    def __init__(self):
        self.conn = MySQLdb.connect(*self.dsn)
        self.cursor = self.conn.cursor()

    def is_phone_exist(self, phone):
        query = "SELECT * FROM dug_table WHERE DUG = %s" % phone
        response = self.cursor.execute(query)
        return response

    def update_table(self, phone):
        command = "INSERT INTO dug_table VALUES (%s)" % phone
        try:
            self.cursor.execute(command)
            self.conn.commit()
            return True
        except:
            return False
    def print_rows(self):
        query = "SELECT COUNT(*) FROM dug_table"
        response = self.cursor.execute(query)
        total_counts = self.cursor.fetchall()
        print(np.squeeze(total_counts))

    def __del__(self):
        self.conn.close()

def facebook_login(email, passw):
    # Initializing the chrome
    chrome_options = webdriver.ChromeOptions()
    prefs = {"profile.default_content_setting_values.notifications" : 2}
    chrome_options.add_experimental_option("prefs",prefs)
    if platform.system() == "Windows":
        driver = webdriver.Chrome(executable_path="resource/chromedriver.exe", chrome_options=chrome_options)
    else:
        driver = webdriver.Chrome(chrome_options=chrome_options)
    # Log-in
    driver.get("http://www.facebook.com")
    emailField = driver.find_element_by_id("email")
    if emailField:
        emailField.send_keys(email)
    else:
        print("Could not find Email Field")
        return False
    passField = driver.find_element_by_id("pass")
    if passField:
        passField.send_keys(passw)
    else:
        print("Could not find Password Field")
        return False
    try:
        loginBtn = driver.find_element_by_id("u_0_s")
        loginBtn.click()
    except:
        try:
            loginBtn = driver.find_element_by_id("u_0_q")
            loginBtn.click()
        except:
            try:
                loginBtn = driver.find_element_by_xpath("//input[@value='Log In']")
                loginBtn.click()
            except:
                print("Could not find Log-in Button")
                return False
    return driver

def read_settings():
    if platform.system() == "Windows":
        with open("resource\\settings_win.json") as data_file:
                settings = json.load(data_file)
    else:
        with open("resource/settings_linux.json") as data_file:
                settings = json.load(data_file)
    return settings

def save_page(fn, content):
    html = open(fn, "wb")
    html.write(content.encode('utf-8'))
    html.close()


# Start of Script

settings = read_settings()

max_profile = int(settings['max_profile'])
phone_file = settings['phone_file']
fb_account = settings['fb_account']
fb_folder = settings['output_folder']


df = pd.read_csv(phone_file, dtype=object, usecols=['DUG'])
df = df.sample(frac=1).reset_index(drop=True)
fb_df = pd.read_csv(fb_account)

phone_db = sql()

phone_db.print_rows()

for index, acc in fb_df.iterrows():

    email = acc['id']
    passw = acc['pass']

    driver = facebook_login(email, passw)

    if driver == False:
        print(email,': Login Problem ( login id unknown)')
        driver.close()
        continue

    if "login_attempt" in driver.current_url:
        print(email,': Account disabled')
        driver.close()
        continue

    if "checkpoint" in driver.current_url:
        print(email,': Account Blocked')
        driver.close()
        continue

    total = 0;

    for phone in df['DUG']:
        phone = str(phone)
        phone = phone[:8]
        if phone_db.is_phone_exist(str(phone)):
            continue
        elif total > max_profile:
            print(email,": Max profile reached")
            break
        else:
            fn = fb_folder + str(phone) + '.html'
            if os.path.isfile(fn):
                continue
            else:
                total = total + 1
                driver.get("https://www.facebook.com/search/top/?q=00976" + str(phone))
                current_url = driver.current_url
                if str(phone) in current_url:
                    content = driver.page_source
                    soup = bs.BeautifulSoup(content)
                    security = soup.find('div',{"id":"captcha"})
                    if security:
                        print(email,": Security Captcha Check")
                        break
                    else:
                        phone_db.update_table(str(phone))
                        save_page(fn, content)
                else:
                    print(email,": Problem with the account")
                    break

    print(email,':' ,str(total))
    driver.close()
    break

phone_db.print_rows()
del phone_db
