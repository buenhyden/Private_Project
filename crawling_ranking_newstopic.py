import sys
sys.path.append('/home/ubuntu/personal_project/')
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
import Database_Handler as dh
from multiprocessing import Pool
from functools import partial
import chat_bot as cb

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


def Realtime_Daum(url):
    searchTime = datetime.now()
    dateIs = searchTime.strftime('%Y-%m-%d')
    timeIs = searchTime.strftime('%H:%M:%S')
    soup = WebPageUsingBS(url, 'html')
    realtimeIssue = soup.find('div', class_='aside_search')
    tit_news = realtimeIssue.find('h3', class_='tit_news').text
    cont_aside = realtimeIssue.find('ul', class_='tab_aside').find_all('div', class_='cont_aside')
    return dateIs, timeIs, cont_aside


def SearchNewstopicForDaum(date, time, soup_ul_div):
    category = soup_ul_div.find('strong', class_='screen_out').text
    list_ranking = list(
        map(lambda x: (date, time, 'daum', category, x.find('em').text, x.find('a').text), soup_ul_div.find_all('li')))
    rank_Df = pd.DataFrame(list_ranking)
    rank_Df.rename({0: 'date', 1: 'time', 2: 'site', 3: 'category', 4: 'rank', 5: 'topic'}, inplace=True, axis=1)
    return rank_Df


def Main_Daum():
    url = Resource()[0]
    realTime = Realtime_Daum(url)
    out_Dfs = pd.DataFrame(columns=['date', 'time', 'site', 'category', 'rank', 'topic'])
    for categoryTopic in realTime[2]:
        newsTopics = SearchNewstopicForDaum(realTime[0], realTime[1], categoryTopic)
        if len(out_Dfs) == 0:
            out_Dfs = newsTopics
        else:
            out_Dfs = pd.concat([out_Dfs, newsTopics], axis=0)
    out_Dfs.reset_index(drop=True, inplace=True)
    return out_Dfs


def Realtime_Naver(url):
    searchTime = datetime.now()
    dateIs = searchTime.strftime('%Y-%m-%d')
    timeIs = searchTime.strftime('%H:%M:%S')
    soup = WebPageUsingBS(url, 'html')
    realtimeIssue = soup.find('td', class_='aside').find('div', class_='hottopic')
    categoryIssues = realtimeIssue.find_all('ol', class_='type15')
    return dateIs, timeIs, categoryIssues


def Category_Topic(x):
    if x == 'newstopic_news':
        y = r'뉴스'
    else:
        y = r'연예/스포츠'
    return y


def SearchNewstopicForNaver(date, time, soup_ul_div):
    category = Category_Topic(soup_ul_div.attrs['id'])
    list_ranking = list(map(lambda x: (date, time, 'naver', category, x.find('em').text, x.find('a')['title']),
                            soup_ul_div.find_all('li')))
    rank_Df = pd.DataFrame(list_ranking)
    rank_Df.rename({0: 'date', 1: 'time', 2: 'site', 3: 'category', 4: 'rank', 5: 'topic'}, inplace=True, axis=1)
    return rank_Df


def Main_Naver():
    url = Resource()[1]
    realTime = Realtime_Naver(url)
    out_Dfs = pd.DataFrame(columns=['date', 'time', 'site', 'category', 'rank', 'topic'])
    for categoryTopic in realTime[2]:
        newsTopics = SearchNewstopicForNaver(realTime[0], realTime[1], categoryTopic)
        if len(out_Dfs) == 0:
            out_Dfs = newsTopics
        else:
            out_Dfs = pd.concat([out_Dfs, newsTopics], axis=0)
    out_Dfs.reset_index(drop=True, inplace=True)
    return out_Dfs


def Resource():
    daumWebpath = 'http://media.daum.net/ranking/popular/'
    naverWebpath = 'http://news.naver.com/main/ranking/popularDay.nhn?'
    return daumWebpath, naverWebpath

def Main(site,db_name):
    mongodb = dh.ToMongoDB(*dh.AWS_MongoDB_Information())
    dbname = db_name
    useDb = dh.Use_Database(mongodb, dbname)
    slack = cb.Slacker(cb.slacktoken())
    startTime = datetime.now()
    if site.lower() == 'naver':
        topicDf = Main_Naver()
    elif site.lower() == 'daum':
        topicDf = Main_Daum()
    else:
        raise NotMatch('Not Match site')
    middleTime = datetime.now()
    runningTime = middleTime = middleTime - startTime
    print ('Start Uploading')
    useCollection_comment = dh.Use_Collection(useDb, 'newsTopics')
    useCollection_comment.insert_many(topicDf.to_dict('records'))
    print ('End Uploading')
    endTime = datetime.now()
    uploadTime = endTime - middleTime
    outcome_info = 'News Topics {}, run date : {}, Number : {} Complete Upload in AWS mongodb'.format(site, startTime.strftime('%Y%m%d'), len(topicDf)))
    slack.chat.post_message('# notification', outcome_info)
    mongodb.close()

if __name__ == '__main__':
    sites = ['daum','naver']
    p = Pool(2)
    x = partial(Main, db_name = 'hy_db')
    p.map(x, sites)
