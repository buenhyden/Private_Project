import sys
sys.path.append('C:/Users/pc/Documents/GitHub/Private_Project/personal_project')
from collections import defaultdict
from datetime import datetime, timedelta
import time
import re
import requests
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
import pickle
import chat_bot as cb
import Database_Handler as dh
def isElementPresent(driver, locator):
    try:
        driver.find_element_by_class_name(locator)
    except NoSuchElementException:
        return False
    return True
def SearchKeywordsFromDaumForNaver(title, press):
    driver = webdriver.Chrome('C:/Users/pc/Documents/chromedriver.exe')
    driver.get('http:www.daum.net')
    tf_keyword = title + '&' + press
    element = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.CLASS_NAME, 'tf_keyword')))
    element.send_keys(tf_keyword)
    button = driver.find_element_by_css_selector('#daumSearch > fieldset > div > div > button')
    webdriver.ActionChains(driver).move_to_element(button).click(button).perform()
    try:
        webpage = driver.find_element_by_css_selector('#clusterResultUL > li > div.wrap_cont > div > span > a').get_attribute('href')
        driver.get(webpage)
        element = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.CLASS_NAME, 'copyright_view')))
    except:
        keywords = 'NaN'
        driver.quit()
        return keywords
    else:
        if isElementPresent(driver, 'tag_relate') == False:
            keywords = 'NaN'
        else:
            element = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.CLASS_NAME, 'tag_relate')))
            keywords = driver.find_elements_by_class_name('tag_relate')
            keywords = list(map(lambda x: x.text, keywords))
            keywords = list(map(lambda x: re.sub('#', '', x), keywords))
    driver.quit()
    return keywords

if __name__=='__main__':
    site = 'Naver'
    collection = 'newsNaver'
    mongodb = dh.ToMongoDB(*dh.AWS_MongoDB_Information())
    dbname = 'hy_db'
    useDb = dh.Use_Database(mongodb, dbname)
    slack = cb.Slacker(cb.slacktoken())
    useCollection = dh.Use_Collection(useDb, collection)
    dataList = useCollection.find({'site': site})
    for data in dataList:
        if not 'keywords' in data.keys() :
            keywords = SearchKeywordsFromDaumForNaver(data['title'], data['press'])
            useCollection.update({"_id": data['_id']},
            {'$set': {"keywords": keywords}})