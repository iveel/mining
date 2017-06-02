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
import MySQLdb

warnings.filterwarnings('ignore')


class sql:
    def __init__(self):
        db = MySQLdb.connect(host='sql8.freemysqlhosting.net', user='sql8177810',\
                            passwd = '4MeU7jpiBz',db = 'sql8177810', port = 3306)
        self.cursor = db.cursor()

    def is_phone_exist(phone):
        query = "SELECT * FROM dug_table WHERE DUG = %s" % phone
        response = self.cursor.execute(query)
        return response

    def update_table(phone):
        command = "INSERT INTO dug_table VALUES (%s)" % phone
        try:
            self.cursor.execute(command)
            db.commit()
            return True
        except:
            return False

    def __del__(self):
        self.cursor.close()
        db.close()


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
    loginBtn = driver.find_element_by_id("u_0_s")
    if loginBtn:
        loginBtn.click()
    else:
        loginBtn = driver.find_element_by_id("u_0_q")
        if loginBtn:
            loginBtn.click()
        else:
            loginBtn = driver.find_element_by_xpath("//input[@value='Log In']")
            if loginBtn:
                loginBtn.click()
            else:
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
