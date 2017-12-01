import sys
# sys.path.append('/home/ubuntu/personal_project/project/')
from collections import defaultdict
from datetime import datetime
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


# [Default]
def OpenAPI(apiFile):
    apiKey = pickle.load(open(apiFile, 'rb'))
    return apiKey


## Define Error
class NotMatch(Exception):
    def __init__(self, f):
        self.f = f

    def __str__(self):
        return self.f


## Setting BeautifulSoup
def Setting_BeautifulSoup(parser):
    if parser.lower() == 'xml':
        parser = 'lxml'
    elif parser.lower() == 'html':
        parser = 'html.parser'
    else:
        raise NotMatch('Not Match parser')
    return parser


## Using BeautifulSoup
def WebPageUsingBS(url, htmltype, openApi=None):
    htmltype = Setting_BeautifulSoup(htmltype)
    if openApi == None:
        response = requests.get(url)
    else:
        response = requests.get(url, headers=openApi)
    soup = BeautifulSoup(response.content, htmltype)
    return soup


# --------------------------------------------------------------------
# Crawling for Naver
# --------------------------------------------------------------------
# Resource for Naver
def Resource_Naver():
    apiInfo = OpenAPI('./naverClient_Info.json')

    basePage = 'http://news.naver.com'
    targetPage = 'http://news.naver.com/main/ranking/popularDay.nhn?'
    return apiInfo, basePage, targetPage


# Search for Date
def SearchDateForNaver(mainpage, url):
    webpage = WebPageUsingBS(url, 'xml')
    dateInfo = webpage.find('div', class_='calendar_date')
    today = dateInfo.find(class_='c_date').text
    yesterdayPage = dateInfo.find('a').attrs['href']
    targetPage = mainpage + yesterdayPage
    webpage2 = WebPageUsingBS(targetPage, 'xml')
    dateInfo2 = webpage2.find('div', class_='calendar_date')
    targetDate = dateInfo2.find(class_='c_date').text
    return targetDate, today, targetPage


# Search for category Name & web path
def SearchTarget(date, mainpage, form):
    category = re.search(r'[a-zA-Z가-힣/]+', form.text).group()
    if category == r'연예':
        targetDay = '-'.join(date.split('.'))[:-1]
        link = mainpage + form.find('a').attrs['href'] + '#type=hit_total&date=' + targetDay
    else:
        link = link = mainpage + form.find('a').attrs['href']
    return {'category': category, 'link': link}


# Search for category web path
def CategoryWebPathForNaver(date, mainpage, url):
    webPage = WebPageUsingBS(url, 'xml')
    category = webPage.find('ul', class_='massmedia').findAll('li')[1:-2]
    outDf = pd.DataFrame(list(map(lambda x: SearchTarget(date, mainpage, x), category)))
    return outDf


# Search for news list in category
def NewsListInCategoryForNaver(date, mainpage, cat, url):
    if cat == r'연예':
        driver = webdriver.PhantomJS('../phantomjs-2.1.1/bin/phantomjs')
        # driver = webdriver.Chrome('../chromedriver')
        driver.get(url)
        newsSelector = '#ranking_list > li > div.tit_area'
        element = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CSS_SELECTOR, newsSelector)))
        newsList = driver.find_elements_by_css_selector(newsSelector)
        outDf = pd.DataFrame(list(map(lambda x: EntertainNewsDataInNaver(date, x), enumerate(newsList))))
        driver.quit()
    else:
        webPage = WebPageUsingBS(url, 'xml')
        newsSelector = '#wrap > table > tr > td > div > div > ol > li > dl'
        newsList = webPage.select(newsSelector)
        outDf = pd.DataFrame(list(map(lambda x: NewsDataInNaver(date, cat, mainpage, x), enumerate(newsList))))
    return outDf


# Search for Entertain news Information
def EntertainNewsDataInNaver(date, source):
    rank = source[0] + 1
    title = source[1].find_element_by_class_name('tit').text
    link = source[1].find_element_by_tag_name('a').get_attribute('href')
    return {'date': date, 'rank': rank, 'title': title, 'link': link}


# Search for news Information
def NewsDataInNaver(date, cat, mainpage, source):
    rank = source[0] + 1
    if cat == r'스포츠':
        link = source[1].find('a').attrs['href']
    else:
        link = mainpage + source[1].find('a').attrs['href']
    title = source[1].find('a').attrs['title']
    return {'date': date, 'rank': rank, 'title': title, 'link': link}


# Filtering News Article
def FilterMainText(contents):
    body = re.sub('(<span.*?>.*?</span>)', '', str(contents))
    mainText = re.sub('<.+?>', '', body, 1)
    mainText = mainText.replace(u'\xa0', u'')
    mainText = mainText.split('<br/><br/>')
    mainText = list(map(lambda x: re.sub('<a.*?>.*?</a>', '', x), mainText))
    mainText = list(filter(lambda x: re.search('(<.+?>)', x) == None, mainText))
    mainText = list(filter(lambda x: x != '', mainText))
    mainText = list(map(lambda x: x.strip(), mainText))
    mainText = ''.join(mainText)
    return mainText


# Search for News Article & Press
def ArticleInNaver(cat, url):
    if cat == r'연예':
        mainTextId = 'articeBody';
        pressClass = 'press_logo'
    elif cat == r'스포츠':
        mainTextId = 'newsEndContents';
        pressClass = 'logo'
    else:
        mainTextId = 'articleBodyContents';
        pressClass = 'press_logo'
    webPage = WebPageUsingBS(url, 'xml')
    mainText = webPage.find('div', id=mainTextId)
    mainText = FilterMainText(mainText)
    press = webPage.find(class_=pressClass)
    press = press.find('img').attrs['alt']
    return mainText, press


# Search for Comment
def CommentInNaver(cat, url):
    # driver = webdriver.PhantomJS('../phantomjs-2.1.1/bin/phantomjs')
    driver = webdriver.Chrome('../chromedriver')
    if cat == r'연예':
        commentByClass = 'reply_count';
        commentNumByClass = 'u_cbox_count'
    elif cat == r'스포츠':
        commentByClass = 'comment';
        commentNumByClass = 'u_cbox_count'
    else:
        commentByClass = 'pi_btn_count';
        commentNumByClass = 'u_cbox_count'
    totalCommmentClass = 'u_cbox_area';
    commentMore = 'u_cbox_paginate'
    driver.get(url)
    element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, commentByClass)))
    moreCommentPage = driver.find_element_by_class_name(commentByClass)
    webdriver.ActionChains(driver).move_to_element(moreCommentPage).click(moreCommentPage).perform()
    element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, commentNumByClass)))
    commentNum = driver.find_element_by_class_name(commentNumByClass).text
    print('Number of comment : {}'.format(commentNum))
    print('Start : Click More Button')
    loop = True
    while loop == True:
        try:
            element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, commentMore)))
            moreComment = driver.find_element_by_class_name(commentMore)
            webdriver.ActionChains(driver).move_to_element(moreComment).click(moreComment).perform()
            driver.implicitly_wait(1)
            if moreComment.get_attribute('style') != '':
                loop = False
        except TimeoutException:
            try:
                element = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, commentMore)))
                moreComment = driver.find_element_by_class_name(commentMore)
                webdriver.ActionChains(driver).move_to_element(moreComment).click(moreComment).perform()
            except NoSuchElementException:
                loop = False
    print('End Click More Button & Start Crawling comments')
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    commentsList = soup.find_all(class_=totalCommmentClass)
    # commentsDf=pd.DataFrame(commentsList)[[1,3]]
    time.sleep(3)
    commentsDf = pd.DataFrame({'comments': soup.find_all(class_='u_cbox_contents'),
                               '공감': soup.find_all(class_='u_cbox_btn_recomm'),
                               '비공감': soup.find_all(class_='u_cbox_btn_unrecomm')
                               })
    driver.quit()
    commentsDf = commentsDf.apply(lambda x: ExtractElementFromRow(x), axis=1)
    return commentsDf


def ExtractElementFromRow(row):
    row['comments'] = row['comments'].text
    row['공감'] = row['공감'].select_one('em').text
    row['비공감'] = row['비공감'].select_one('em').text
    return row


# Extract Comments
def ExtractComments(class1, class2):
    try:
        commentText = class1.find(class_='u_cbox_contents').text
        recomm = class2.find(class_='u_cbox_btn_recomm').select_one('em').text
        unrecomm = class2.find(class_='u_cbox_btn_unrecomm').select_one('em').text
    except:
        pass

    return pd.DataFrame({'comments': commentText, r'공감': recomm, r'비공감': unrecomm})


# Run in Naver
def Main_Naver():
    naverAPI, basePage, targetPage = Resource_Naver()
    targetDate, todayDate, pageForTargetDate = SearchDateForNaver(basePage, targetPage)
    print('Site : {}, Run Date : {}, Goal Date : {}'.format('Naver', todayDate, targetDate))
    categoryInRankingNews = CategoryWebPathForNaver(targetDate, basePage, pageForTargetDate)
    outNews = pd.DataFrame()
    outComment = pd.DataFrame()
    for idx in categoryInRankingNews.index:
        data = categoryInRankingNews.loc[idx]
        category = data['category']
        print(category)
        link = data['link']
        newsList = NewsListInCategoryForNaver(targetDate, basePage, category, link)
        newsList = pd.concat([pd.DataFrame([category] * len(newsList), columns=['category']), newsList], axis=1)
        newsList['press'] = ''
        newsList['mainText'] = ''
        for idx2 in newsList.index:
            print(idx2)
            newsInfo = ArticleInNaver(category, newsList.loc[idx2]['link'])
            newsList.loc[idx2, 'press'] = newsInfo[1]
            newsList.loc[idx2, 'mainText'] = newsInfo[0]
            comments = CommentInNaver(category, newsList.loc[idx2]['link'])
            baseDf = pd.DataFrame({'category': [newsList.loc[idx2]['category']] * len(comments),
                                   'date': [newsList.loc[idx2]['date']] * len(comments),
                                   'rank': [newsList.loc[idx2]['rank']] * len(comments)})
            commentsList = pd.concat([baseDf, comments], axis=1)
            outComment = pd.concat([outComment, commentsList], axis=0)
        outNews = pd.concat([outNews, newsList], axis=0)
    return outNews, outComment


if __name__ == "__main__":
    start = time.time()
    x = Main_Naver()
    end = time.time()