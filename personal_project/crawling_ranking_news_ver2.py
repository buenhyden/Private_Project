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

def SearchTarget(form):
    category = re.search(r'[a-zA-Z가-힣/]+', form.text).group()
    link = form.find('a').attrs['href']
    return category, link

def CategoryWebPath(url):
    webPage  = WebPage(url, 'lxml')
    category = webPage.find('ul',class_='massmedia').findAll('li')[1:-2]
    outdict = dict()
    for mass in enumerate(category):
        formIs = SearchTarget(mass[1])
        outdict[formIs[0]] = formIs[1]
    return outdict

def NewsDataInNaver(date, source):
    rank = source[0]+1
    link = source[1].find('a').attrs['href']
    title = source[1].find('a').attrs['title']
    return {'date':date, 'rank':rank,'title':title, 'link':link}


def NewsListInCategory(date,cat,url):
    webPage = WebPage(url,'lxml')
    newsSelector = '#wrap > table > tr > td > div > div > ol > li > dl'
    newsList = webPage.select(newsSelector)
    dp = pd.DataFrame(columns=['date','rank', 'title', 'link'])
    for news in enumerate(newsList):
        NewsInfo = NewsDataInNaver(date, news)
        dp.loc[len(dp)] = NewsInfo
    return dp

def NewsListInCategoryEntertain(date,cat,url):
    driver = WebDriver(url)
    targetDay = '-'.join(date.split('.'))[:-1]
    targetDaySelector = '#newsWrp > div.pagenavi_day > a'
    targetDays = driver.find_elements_by_css_selector(targetDaySelector)
    out = list(filter(lambda x: x.get_attribute('data-day')==targetDay, targetDays))[0]
    print (out)
    out.click()
    #newsSelector = '#wrap > table > tr > td > div > div > ol > li > dl'
    time.sleep(1)
    newsSelector = '#ranking_list > li > div.tit_area'
    newsList = driver.find_elements_by_css_selector(newsSelector)
    dp = pd.DataFrame(columns=['date','rank', 'title', 'link'])
    for news in enumerate(newsList):
        rank = news[0]+1
        title = news[1].find_element_by_class_name('tit').text
        link = news[1].find_element_by_tag_name('a').get_attribute('href')
        print (rank, title, link)
        dp.loc[len(dp)] = {'date':date, 'rank':rank,'title':title, 'link':link}
    driver.quit()
    return dp

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
    element = WebDriverWait(driver,3).until(EC.presence_of_element_located((By.CLASS_NAME,'u_cbox_btn_view_comment')))
    print ('Searching more comment point')
    numComment = driver.find_element_by_class_name('u_cbox_info_txt').text
    commentButton = driver.find_element_by_class_name('u_cbox_btn_view_comment')
    webdriver.ActionChains(driver).move_to_element(commentButton).click(commentButton).perform()
    print ('Number of comment : {}'.format(numComment))
    time.sleep(1)
    print ('Start : Search Sort Favorite Button')
    sortButtons = driver.find_elements_by_css_selector('#cbox_module > div > div.u_cbox_sort > div.u_cbox_sort_option > div > ul > li > a')
    favoriteButton = list(filter(lambda xx: xx.get_attribute('data-param') == 'favorite', sortButtons))[0]
    favoriteButton.click()
    print ('End : Search Sort Favorite Button')
    time.sleep(1)
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
    return outDict

def SearchDate(mainpage, url):
    webpage = WebPage(url, 'lxml')
    dateInfo = webpage.find('div', class_='calendar_date')
    today = dateInfo.find(class_='c_date').text
    yesterdayPage = dateInfo.find('a').attrs['href']
    targetPage = mainpage+yesterdayPage
    webpage2 = WebPage(targetPage, 'lxml')
    dateInfo2 = webpage2.find('div', class_='calendar_date')
    targetDate = dateInfo2.find(class_='c_date').text
    return targetDate, targetPage

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
def Resource_Naver():
    apiInfo = OpenAPI('./naverClient_Info.json')
    mainPage = 'http://news.naver.com'
    webpage = 'http://news.naver.com/main/ranking/popularDay.nhn?'
    runDate = datetime.now()
    return apiInfo, mainPage, webpage, runDate

def Resource_Daum():
    newPage = 'http://media.daum.net/ranking/popular/'
    mainPage = 'http://media.daum.net'
    runDate = datetime.now()
    return mainPage,newPage, runDate

def SearchRanking(url):
    soup = WebPage(url, 'lxml')
    date = soup.find(class_='box_calendar')
    todayIs = date.find(class_='screen_out').text
    compileIs = re.compile('[\d]+')
    todayIs = '.'.join(compileIs.findall(todayIs))
    yesterdayIs = soup.select_one('a.btn_date.btn_prev').attrs['href']
    return todayIs, yesterdayIs

def PopularPage(mainPage, url):
    link = mainPage+url
    soup = WebPage(link, 'lxml')
    date = soup.find(class_='box_calendar')
    compileIs = re.compile('[\d]+')
    targetDate = date.find(class_='screen_out').text
    targetDate = '.'.join(compileIs.findall(targetDate))
    targetList = soup.select('#mArticle > div.rank_news > ul.tab_sub > li > a')[1:]
    outDict = dict()
    for target in targetList:
        category = target.text.strip()
        link = target.attrs['href']
        outDict[category]=mainPage+link
    return targetDate, outDict

def NewsData(date, source):
    rank = source.find('span', class_='screen_out').text
    press = source.find('span', class_='info_news').text
    title = source.find('a', class_='link_txt').text
    link = source.find('a', class_='link_txt').attrs['href']
    return {'date': date, 'rank': rank, 'press': press, 'title': title, 'link': link}

def NewsListInCategoryInDaum(date, url):
    soup = WebPage(url, 'html.parser')
    newsList = soup.select('#mArticle > div.rank_news > ul.list_news2 > li')
    outdict = dict()
    dp = pd.DataFrame(columns=['date', 'rank', 'press', 'title', 'link'])
    for news in newsList:
        x = NewsData(date, news)
        dp.loc[len(dp)] = x
    # return outdict
    return dp

def NewsArticle(url):
    driver = WebDriver(url)
    article = driver.find_element_by_class_name('news_view').text
    keywords = driver.find_elements_by_css_selector('#mArticle > div.foot_view > div.relate_tag.hc_news_pc_mArticle_relatedTags > span > a > span')
    keywords = list(map(lambda x: x.text, keywords))
    keywords = list(filter(lambda x: re.sub('#','',x), keywords))
    try:
        recomm = '//*[@id="alex-area"]/div/div/div/div[3]/ul[1]/li[1]/button'
        element = WebDriverWait(driver, 1).until(
            EC.presence_of_element_located(
                (By.XPATH, recomm))
        )
        element.click()
    except:pass
    else:
        try:
            element = WebDriverWait(driver, 2).until(
                EC.presence_of_element_located(
                    (By.ID,'alex-area'))
            )
        except:
            pass
        else:
            loop = True
            while loop:
                try:
                    element = WebDriverWait(driver, 3).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, "#alex-area > div > div > div > div.cmt_box > div.alex_more > a"))
                )
                    more_button = driver.find_element_by_css_selector(
                        "#alex-area > div > div > div > div.cmt_box > div.alex_more > a")
                    webdriver.ActionChains(driver).click(more_button).perform()
                    break
                except:
                    loop = False
            comment_box = driver.find_element_by_css_selector(
                "#alex-area > div > div > div > div.cmt_box > ul.list_comment")
            comment_list = comment_box.find_elements_by_tag_name("li")
            comment_list = list(map(lambda x: CommentsInDaum(x), comment_list))
    driver.quit()
    return keywords, article, comment_list

def CommentsInDaum(ss):
    comments = ss.find_element_by_tag_name('p').text
    recomm = ss.find_element_by_class_name('comment_recomm')
    like = recomm.find_element_by_xpath('button[1]').text
    dislike = recomm.find_element_by_xpath('button[2]').text
    like = (r'공감',like.split('\n')[1])
    dislike = (r'비공감', dislike.split('\n')[1])
    return comments, dict([like, dislike])

if __name__ == "__main__":
    resourceDaum = Resource_Daum()
    x = SearchRanking(resourceDaum[1])
    y = PopularPage(resourceDaum[0],x[1])
    for i in y[1]:
        print (i,y[1][i])
        z = NewsListInCategoryInDaum(y[1][i])
        for ii in z:
            print (ii,z[ii])
            break
            qq = NewsArticle((z[ii]['link']))
            print (qq)

            break
        break
        '''
    resource = Resource_Naver()
    dateInfo = SearchDate(resource[1], resource[2])
    print ('Crawling Date : {}'.format(resource[3]))
    print ('Crawling Target Date : {}'.format(dateInfo[0]))
    category = CategoryWebPath(dateInfo[1])
    for cat in category:
        print (cat)
        link = resource[1]+category[cat]
        newsList = NewsListInCategory(dateInfo[0],cat, link)
        print (newsList)
        for idx in newsList:
            newsLink = resource[1]+newsList[idx]['link']
            print (newsLink)
            articleText = Article(newsLink)
            print (articleText)
            comments = Comments(newsLink)
        break
    '''