#
# Reference : https://github.com/forkonlp/N2H4
# chage from R code to Python code
#
import sys
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from datetime import datetime, timedelta
import pickle
import json
import chat_bot as cb
import Database_Handler as dh
import html
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import itertools
import multiprocessing

def OS_Driver(os,browser):
    if os.lower() == 'windows':
        if browser.lower() == 'phantom':
            driver = webdriver.PhantomJS('C:/Users/pc/Documents/phantomjs-2.1.1-windows/bin/phantomjs.exe')
        else:
            driver = webdriver.Chrome('C:/Users/pc/Documents/chromedriver.exe')
    elif os.lower() == 'mac':
        if browser.lower() == 'phantom':
            driver = webdriver.PhantomJS(
                '/Users/hyunyoun/Documents/GitHub/Private_Project/phantomjs-2.1.1/bin/phantomjs')
        else:
            driver = webdriver.Chrome('/Users/hyunyoun/Documents/GitHub/Private_Project/chromedriver')
    return driver
# Use naver api
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

class Crawling_In_Naver():
    def __init__(self, date):
        self.date = datetime.strptime(str(date), '%Y%m%d')
        self.targetPage = 'http://news.naver.com/main/ranking/popularDay.nhn?rankingType=popular_day&date='+ self.date.strftime('%Y%m%d')
        self.basePage = 'http://news.naver.com'
        self.EnterPage = 'http://entertain.naver.com'
    def Category_And_Link(self):
        source = requests.get(self.targetPage)
        soup = BeautifulSoup(source.content, 'lxml')
        category = soup.find('ul',class_='massmedia').find_all('li')[1:-2]
        df_category = pd.DataFrame({'category' : list(map(lambda x: x.text, category)),
                                    'link' : list(map(lambda x: self.basePage + re.sub('§','&',x.find('a').attrs['href']), category))})
        df_category.set_index('category',inplace=True)
        df_category.loc['연예']['link'] = re.sub('news', 'entertain', df_category.loc['연예']['link'])
        df_category.loc['연예']['link'] = re.sub('main/ranking/popularDay.nhn', 'ranking', df_category.loc['연예']['link'])+'#type=hit_total&date=' + self.date.strftime('%Y-%m-%d')
        return df_category
    def NewsList(self,cat):
        df_category = Crawling_In_Naver(self.date.strftime('%Y%m%d')).Category_And_Link()
        source2 = requests.get(df_category.loc[cat]['link'])
        soup2 = BeautifulSoup(source2.content, 'html.parser')
        newslist = soup2.find('div', class_='content').select('div > ol > li > dl > dt > a')
        raw_newslist = list(map(lambda x: self.basePage + x.attrs['href'], newslist))
        newslist_1 = pd.DataFrame({'link' : raw_newslist})
        newslist_2 = pd.DataFrame(list(map(lambda y: dict(map(lambda x: re.split('=', x) ,re.split('&', y))), raw_newslist)))
        newslist = pd.merge(newslist_1,newslist_2, left_index=True, right_index=True)
        newslist.drop('rankingSeq', axis = 1, inplace = True)
        newslist.drop('date',axis = 1, inplace = True)
        newslist.drop('http://news.naver.com/main/ranking/read.nhn?mid', axis = 1, inplace=True)
        newslist.drop('rankingType',axis = 1, inplace = True)
        newslist.drop('type', axis = 1, inplace = True)
        newslist.drop('rankingSectionId', axis = 1, inplace = True)
        return newslist
    def SportsNewsList(self):
        df_category = Crawling_In_Naver(self.date.strftime('%Y%m%d')).Category_And_Link()
        source2 = requests.get(df_category.loc['스포츠']['link'])
        soup2 = BeautifulSoup(source2.content, 'html.parser')
        newslist = soup2.find('div', class_='content').select('div > ol > li > dl > dt > a')
        raw_newslist = list(map(lambda x: x.attrs['href'], newslist))
        newslist_1 = pd.DataFrame({'link' : raw_newslist})
        newslist_2 = pd.DataFrame(list(map(lambda y: dict(map(lambda x: re.split('=', x) ,re.split('&', y))), raw_newslist)))
        newslist = pd.merge(newslist_1,newslist_2, left_index=True, right_index=True)
        newslist.drop('http://sports.news.naver.com/sports/index.nhn?ctg', axis = 1, inplace = True)
        newslist.drop('mod', axis = 1, inplace = True)
        newslist.drop('ranking_type', axis = 1, inplace = True)
        newslist.drop('date',axis = 1, inplace = True)
        newslist.rename({'article_id' : 'aid', 'office_id':'oid'}, axis = 1, inplace = True)
        return newslist
    def EntertainNewsList(self):
        df_category = Crawling_In_Naver(self.date.strftime('%Y%m%d')).Category_And_Link()
        driver = OS_Driver('windows','chrome')
        driver.get(df_category.loc['연예']['link'])
        soup2 = BeautifulSoup(driver.page_source, 'html.parser')
        newsSelector = '#ranking_list > li > div.tit_area'
        driver.quit()
        newslist = soup2.select(newsSelector)
        raw_newslist = list(map(lambda x: self.EnterPage+x.find('a').attrs['href'], newslist))
        newslist_1 = pd.DataFrame({'link' : raw_newslist})
        newslist_2 = pd.DataFrame(list(map(lambda y: dict(map(lambda x: re.split('=', x) ,re.split('&', y))), raw_newslist)))
        newslist = pd.merge(newslist_1,newslist_2, left_index=True, right_index=True)
        newslist.rename({'http://entertain.naver.com/ranking/read?oid':'oid'}, axis = 1, inplace = True)
        return newslist

class GetContents:
    def __init__(self, data, cat):
        self.cat = cat
        self.data = data

    def GetAllContents(self):
        self.driver = OS_Driver('windows', 'chrome')
        self.driver.get(self.data['link'])
        pressClassList = ['logo', 'press_logo']
        if self.cat == r'연예':
            mainTextId = 'articeBody'
            title = self.driver.find_element_by_class_name('end_tit').text
        elif self.cat == r'스포츠':
            mainTextId = 'newsEndContents'
            title = self.driver.find_element_by_class_name('title').text
        else:
            mainTextId = 'articleBodyContents'
            title = self.driver.find_element_by_class_name('tts_head').text
        try:
            element = WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.CLASS_NAME, pressClassList[0])))
            press = self.driver.find_element_by_class_name(pressClassList[0]).find_element_by_tag_name(
                'img').get_attribute('alt')
        except:
            element = WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.CLASS_NAME, pressClassList[1])))
            press = self.driver.find_element_by_class_name(pressClassList[1]).find_element_by_tag_name(
                'img').get_attribute('alt')
        articleIdList = ['articeBody', 'newsEndContents', 'articleBodyContents']
        try:
            mainText = self.driver.find_element_by_id(mainTextId)
        except:
            articleIdList.remove(mainTextId)
            try:
                mainText = self.driver.find_element_by_id(articleIdList[0])
            except:
                mainText = self.driver.find_element_by_id(articleIdList[1])
                mainText = re.sub('[\t☞ⓒ]', '', mainText.text)
            else:
                mainText = re.sub('[\t☞ⓒ]', '', mainText.text)
        else:
            mainText = re.sub('[\t☞ⓒ]', '', mainText.text)
        mainText = mainText.replace(u'\xa0', u'')
        mainText = re.sub('\n', ' ', mainText)
        mainText = re.sub('이미지 원본보기', '', mainText)
        mainText = html.unescape(mainText)
        daumSearch = 'https://search.daum.net/search?w=tot&DA=YZR&t__nil_searchbox=btn&sug=&sugo=&q='
        res = requests.get(daumSearch + title)
        soup = BeautifulSoup(res.content, 'html.parser')
        link = soup.select_one('#clusterResultUL > li > div.wrap_cont > div > span > a')
        try:
            self.driver.get(link.attrs['href'])
            element = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, 'tag_relate')))
        except:
            keywords = 'NaN'
        else:
            if isElementPresent(self.driver, 'tag_relate') == False:
                keywords = 'NaN'
            else:
                element = WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'tag_relate')))
                keywords = self.driver.find_elements_by_class_name('tag_relate')
                keywords = list(map(lambda x: x.text, keywords))
                keywords = list(map(lambda x: re.sub('#', '', x), keywords))
        self.driver.quit()
        return title, press, mainText, keywords

    def GetComments(self, pageSize=10, page=1):
        mainPage = "https://apis.naver.com/commentBox/cbox/web_naver_list_jsonp.json?"
        self.pageSize = str(pageSize)
        self.page = str(page)
        if self.cat == r'연예':
            ticket = 'news'
            pool = 'cbox5'
            templateId = 'view_ent'
            useAltSort = ""
            params = {'user-agent': "x",
                      'referer': 'http://entertain.naver.com/main/read.nhn?mode=LSD&mid=shm&oid={}&aid={}'.format(
                          self.data['oid'], self.data['aid'])}
        elif self.cat == r'스포츠':
            ticket = 'sports'
            pool = 'cbox2'
            templateId = 'view'
            useAltSort = ""
            params = {'user-agent': "x",
                      'referer': 'http://news.naver.com/main/read.nhn?mode=LSD&mid=shm&oid={}&aid={}'.format(
                          self.data['oid'], self.data['aid'])}
        else:
            ticket = 'news'
            pool = 'cbox5'
            templateId = 'view_politics'
            useAltSort = "&useAltSort=true"
            params = {'user-agent': "x",
                      'referer': 'http://news.naver.com/main/read.nhn?mode=LSD&mid=shm&sid1={}&oid={}&aid={}'.format(
                          self.data['sid1'], self.data['oid'], self.data['aid'])}
        sort = 'favorite'
        oid = self.data['oid']
        aid = self.data['aid']
        x2 = "ticket=" + ticket;
        x3 = "&templateId=" + templateId;
        x4 = "&pool=" + pool
        x5 = "&lang=ko&country=KR&objectId=news" + oid + "%2C" + aid
        x6 = "&categoryId=&pageSize=" + self.pageSize
        x7 = "&indexSize=10&groupId=&page=" + self.page
        x8 = "&initialize=true" + useAltSort
        x9 = "&replyPageSize=30&moveTo=&sort=" + sort
        page = mainPage + x2 + x3 + x4 + x5 + x6 + x7 + x8 + x9
        res = requests.get(page, headers=params)
        data = BeautifulSoup(res.content, 'html.parser')
        data = data.text
        data = re.sub('_callback', '', data)
        data = re.sub('\(', '[', data)
        data = re.sub('\)', ']', data)
        data = re.sub(';', '', data)
        data = re.sub('\n', '', data)
        data = json.loads(data[1:-1])
        return data

    def GetAllComments(self):
        temp = GetContents(self.data, self.cat).GetComments()
        import math
        numPage = math.ceil(temp['result']['pageModel']['totalRows'] / 100)
        totalCount = sum(list(map(lambda x: temp['result']['count'][x],
                                  ['blindCommentByUser', 'comment', 'delCommentByMon', 'delCommentByUser'])))
        comment = [GetContents(self.data, self.cat).GetComments(100, idx)['result']['commentList'] for idx in
                   range(1, numPage + 1)]
        comment = list(itertools.chain.from_iterable(comment))
        comment = pd.DataFrame(comment)
        return comment, totalCount, comment.shape[0]

def Main_Naver(date):
    print ('Start Crawling')
    crawl = Crawling_In_Naver(date)
    date = datetime.strptime(str(date),'%Y%m%d')
    date = date.strftime('%Y.%m.%d')
    categoryInfo = crawl.Category_And_Link()
    site = 'Naver'
    df_list = list()
    df_comments = pd.DataFrame()
    for idx in range(len(categoryInfo)):
        cat = categoryInfo.index.values[idx]
        print (cat)
        if cat == r'연예':
            contents = crawl.EntertainNewsList()
        elif cat == r'스포츠':
            contents = crawl.SportsNewsList()
        else:
            contents = crawl.NewsList(cat)
        for idx2 in contents.index:
            data = contents.loc[idx2]
            rank = idx2+1
            title, press, mainText, keywords = GetContents(data, cat).GetAllContents()
            comments, nc, rnc = GetContents(data, cat).GetAllComments()
            df_list.append({'category' : cat, 'rank': rank, 'title' : title, 'press' : press, 'keywords' : keywords, 'mainText' : mainText,
                           'number_of_comment' : nc, 'real_number_of_comment' : rnc, 'site' : 'Naver', 'date' : date,
                           'link' : data['link']})
            comments['category'] = cat
            comments['rank'] = rank
            comments['date'] = date
            comments['site'] = site
            df_comments = pd.concat([df_comments, comments], axis = 0)
    outNews = pd.DataFrame(df_list)
    outNews.reset_index(drop=True, inplace = True)
    df_comments.reset_index(drop=True, inplace = True)
    return outNews, df_comments

def Main(site,db_name, runDate, targetDate):
    mongodb = dh.ToMongoDB(*dh.AWS_MongoDB_Information())
    dbname = db_name
    useDb = dh.Use_Database(mongodb, dbname)
    slack = cb.Slacker(cb.slacktoken())
    slack.chat.post_message('# general', 'Start : {}, targetData : {} '.format(site, targetDate))
    startTime = datetime.now()
    newsDf, commentsDf = Main_Naver(targetDate)
    newsCollectionName = 'newsNaver2018'
    middleTime = datetime.now()
    runningTime = middleTime = middleTime - startTime
    print ('Start Uploading')
    useCollection_daum_news = dh.Use_Collection(useDb, newsCollectionName)
    useCollection_daum_news.insert_many(newsDf.to_dict('records'))
    useCollection_comment = dh.Use_Collection(useDb, 'comments2018')
    useCollection_comment.insert_many(commentsDf.to_dict('records'))
    print ('End Uploading')
    endTime = datetime.now()
    uploadTime = endTime - middleTime
    outcome_info = '{}, news : {}, comment : {}'.format(site, len(newsDf), len(commentsDf))
    date_info = 'run date : {}, target date : {}'.format(runDate.strftime('%Y%m%d'), targetDate)
    time_info = 'running time : {}, uploading time'.format(runningTime, uploadTime)
    slack.chat.post_message('# general', outcome_info)
    slack.chat.post_message('# general', date_info)
    slack.chat.post_message('# general', time_info)
    slack.chat.post_message('# general', 'Complete Upload In AWS Mongodb')
    mongodb.close()

if __name__ == "__main__":
    site = 'naver'
    runDate = datetime.now().date()
    targetdate = sys.argv[1]
    Main(site, 'hy_db', runDate, targetdate)
