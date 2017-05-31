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
warnings.filterwarnings('ignore')


def facebook_login(email, passw):
    # Initializing the chrome
    chrome_options = webdriver.ChromeOptions()
    prefs = {"profile.default_content_setting_values.notifications" : 2}
    chrome_options.add_experimental_option("prefs",prefs)
    if platform.system() == "Windows"
        driver = webdriver.Chrome(executable_path="resource/chromedriver.exe", chrome_options=chrome_options)
    else:
        driver = webdriver.Chrome(chrome_options=chrome_options)

    # Log-in
    driver.get("http://www.facebook.com")
    driver.find_element_by_id("email").send_keys(email)
    driver.find_element_by_id("pass").send_keys(passw)
    # driver.find_element_by_id("u_0_s").click()
    driver.find_element_by_xpath("//input[@value='Log In']").click()

    return driver

def read_settings():
    if platform.system() == "Windows":
        with open("git/mining/resource/settings_win.json") as data_file:
                settings = json.load(data_file)
    else:
        with open("git/mining/resource/settings_linux.json") as data_file:
                settings = json.load(data_file)
    return settings


def save_page(fn, content):
    html = open(fn, "wb")
    html.write(content.encode('utf-8'))
    html.close()


# Import Phone list
phone_file = settings['phone_file']
df = pd.read_excel(phone_file)
print(" Phone number is executed ...")

# Import Fb accounts
fb_account = settings['fb_account']
fb_df = pd.read_csv(fb_account)


fb_folder = settings['output_folder']

for index, acc in fb_df.iterrows():
    email = acc['id'] #"osvosos2615337@scramble.io"
    passw = acc['pass'] #"yeyu72052615"

    total = 0;
    s_total = 0;

    driver = facebook_login( email, passw)

    if "checkpoint" in driver.current_url:
        print(email,': Blocked')
        continue


    for phone in df['DUG']:
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
                    break
                else:
                    save_page(fn, content)
            else:
                print("Problem with the account:", email)
                break
    print(email,':' ,str(total))
    driver.close()
