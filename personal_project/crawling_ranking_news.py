import sys
sys.path.append('/home/ubuntu/personal_project/project/')
from collections import defaultdict
from datetime import datetime
import time
import re
import requests
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, ElementNotSelectableException, NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains

def OpenAPI(apiFile):
    import pickle
    apiKey = pickle.load(open(apiFile, 'rb'))
    return apiKey

def WebPage(url,htmltype, openApi = None):
    params = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'
    if openApi == None:
        response = requests.get(url,params = params)
    else:
        response = requests.get(url, headers = openApi, params = params)
    soup = BeautifulSoup(response.content,htmltype)
    return soup

def WebDriver(url):
    driver = webdriver.PhantomJS('/usr/local/bin/phantomjs')
    #driver = webdriver.PhantomJS('/Users/hyunyoun/Documents/GitHub/Private_Project/phantomjs-2.1.1/bin/phantomjs')
    driver.get(url)
    return driver

def CategoryWebPath(url):
    webPage  = WebDriver(url)
    catSelector = '#wrap > table > tbody > tr > td.content > div > div.list_header.ranking_header > div.topbox_type4 > div > ul > li'
    category = webPage.find_elements_by_css_selector(catSelector)[1:-4]
    outdict = dict()
    for mass in category:
        category = re.search(r'[a-zA-Z가-힣/]+',mass.text).group()
        link = mass.find_element_by_tag_name('a').get_attribute('href')
        outdict[category] = link
    webPage.quit()
    return outdict

def NewsListInCategory(cat,url):
    webPage = WebPage(url,'lxml')
    newsSelector = '#wrap > table > tr > td > div > div > ol > li > dl'
    newsList = webPage.select(newsSelector)
    outdict = defaultdict()
    for news in enumerate(newsList):
        rank = news[0]+1
        outdict[rank] = dict()
        link = news[1].find('a').attrs['href']
        title = news[1].find('a').attrs['title']
        outdict[rank]['link'] = link
        outdict[rank]['title'] = title
    return outdict

def Article(url):
    webdriver = WebDriver(url)
    mainText = webdriver.find_element_by_id('articleBodyContents').text
    article = list(filter(lambda x: not x.startswith('▶'), re.split('\n',mainText)))
    article = ''.join(article)
    press = webdriver.find_element_by_css_selector('#main_content > div.article_header > div.press_logo > a > img').get_attribute('title')
    webdriver.quit()
    return article, press

def Comments(url):
    driver = WebDriver(url)
    element = WebDriverWait(driver,2).until(EC.presence_of_element_located((By.CLASS_NAME,'u_cbox_btn_view_comment')))
    print ('Searching more comment point')
    numComment = driver.find_element_by_class_name('u_cbox_info_txt').text
    commentButton = driver.find_element_by_class_name('u_cbox_btn_view_comment')
    webdriver.ActionChains(driver).move_to_element(commentButton).click(commentButton).perform()
    print ('Number of comment : {}'.format(numComment))
    time.sleep(1.5)
    print ('Start : Search Sort Favorite Button')
    sortButtons = driver.find_elements_by_css_selector('#cbox_module > div > div.u_cbox_sort > div.u_cbox_sort_option > div > ul > li > a')
    favoriteButton = list(filter(lambda xx: xx.get_attribute('data-param') == 'favorite', sortButtons))[0]
    favoriteButton.click()
    print ('End : Search Sort Favorite Button')
    time.sleep(1.5)
    loop = True
    print ('Start : Click More Button')
    while loop == True:
        try:
            moreComment = driver.find_element_by_class_name('u_cbox_paginate')
            webdriver.ActionChains(driver).move_to_element(moreComment).click(moreComment).perform()
            time.sleep(0.5)
            if moreComment.get_attribute('style') !='':
                loop=False
        except:
            loop =False
    print ('End : Click More Button')
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()
    commentsList = soup.find_all(class_ = 'u_cbox_area')
    #commentsList = driver.find_elements_by_xpath('//*[@id="cbox_module"]/div/div[8]/ul/li/div/div')
    outDict = dict()
    print ('Number of comment : {}'.format(len(commentsList)))
    print ('Start : Crawling comment')
    for comment in enumerate(commentsList):
        try:
            commentText = comment[1].find(class_='u_cbox_contents').text
            recomm = comment[1].find(class_ = 'u_cbox_btn_recomm')
            recomm = (recomm.select_one('span').text, recomm.select_one('em').text)
            unrecomm = comment[1].find(class_ = 'u_cbox_btn_unrecomm')
            unrecomm = (unrecomm.select_one('span').text, unrecomm.select_one('em').text)
        except:
            pass
        else:
            outDict[comment[0]]=dict()
            outDict[comment[0]]['comment'] = commentText
            outDict[comment[0]].update(dict((recomm,unrecomm)))
    print ('End : Crawling comment')

    '''
    for comment in commentsList:
        try:
            commentText = comment.find_element_by_class_name('u_cbox_contents').text
            recomm = comment.find_element_by_class_name('u_cbox_btn_recomm')
            recomm = (recomm.find_element_by_tag_name('span').text, recomm.find_element_by_tag_name('em').text)
            unrecomm = comment.find_element_by_class_name('u_cbox_btn_unrecomm')
            unrecomm = (unrecomm.find_element_by_tag_name('span').text, unrecomm.find_element_by_tag_name('em').text)
        except NoSuchElementException as nsee:
            pass
        else:
            outDict['comment'] = commentText
            outDict.update(dict((recomm,unrecomm)))
    '''
    return outDict

"""
def JournalistInfo(text):
     pattern = re.compile(r'[가-힣]{2,4}[\W]*기자|[가-힣]{2,4}[\W]*특파원|글:+')
    journalist = pattern.search(text)
    #pattern2 = re.compile(r'[a-zA-z0-9]*@[a-zA-z0-9.]*')
    pattern2 = re.compile(r'([a-zA-z0-9_.]+@)+([0-9a-z\.]+){0,3}')
    email = pattern2.search(text)
    if email==None and journalist==None:
        pass
    else:
        print (email,journalist)
"""

if __name__ == "__main__":
    apiInfo = OpenAPI('./naverClient_Info.json')
    mainPage = 'http://news.naver.com'
    webpage = 'http://news.naver.com/main/ranking/popularDay.nhn?'
    print ("{}".format('Category'))
    category = CategoryWebPath(webpage)
    time.sleep(1)
    for cat in category:
        time.sleep(1)
        print ("category : {}".format(cat))
        x=NewsListInCategory(cat, category[cat])
        for i in x:
            time.sleep(1)
            x2 = mainPage+x[i]['link']
            print (x2)
            articleText = Article(x2)
            print (articleText)
            comments = Comments(x2)
            print (comments)
            break
        break
