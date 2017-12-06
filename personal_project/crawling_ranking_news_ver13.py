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
from multiprocessing import Pool
from functools import partial
# [Default]
def OS_Driver(os):
    if os.lower() == 'windows':
        driver = webdriver.Chrome('C:/Users/pc/Documents/chromedriver.exe')
    elif os.lower() == 'mac':
        driver = webdriver.Chrome('../chromedriver')
    return driver


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
def SearchDateForNaver(targetDate, mainpage, url):
    webpage = WebPageUsingBS(url, 'xml')
    dateInfo = webpage.find('div', class_='calendar_date')
    linkInfo = dateInfo.select_one('a.btn.now')['href']
    targetPage = mainpage + linkInfo + '&date=' + targetDate.strftime('%Y%m%d')
    return targetPage
# Search for category Name & web path
def SearchTargetForNaver(date, mainpage, form):
    category = re.search(r'[a-zA-Z가-힣/]+', form.text).group()
    if category == r'연예':
        #targetDay = '-'.join(date.split('.'))[:-1]
        targetDay = date.strftime('%Y-%m-%d')
        link = mainpage + form.find('a').attrs['href'] + '#type=hit_total&date=' + targetDay
    else:
        link = link = mainpage + form.find('a').attrs['href']
    return {'category': category, 'link': link}
# Search for category web path
def CategoryWebPathForNaver(date, mainpage, url):
    webPage = WebPageUsingBS(url, 'xml')
    category = webPage.find('ul', class_='massmedia').find_all('li')[1:-2]
    outDf = pd.DataFrame(list(map(lambda x: SearchTargetForNaver(date, mainpage, x), category)))
    return outDf
# Search for news list in category
def NewsListInCategoryForNaver(date, mainpage, cat, url):
    if cat == r'연예':
        global os
        driver = OS_Driver(os)
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
    mainText = contents.text
    #body = re.sub('(<span.*?>.*?</span>)', '', str(contents),1)
    #mainText = re.sub('<.+?>', '', body, 1)
    mainText = mainText.replace(u'\xa0', u'')
    #mainText = mainText.split('<br/><br/>')
    #mainText = list(map(lambda x: re.sub('<a.*?>.*?</a>', '', x), mainText))
    #mainText = list(filter(lambda x: re.search('(<.+?>)', x) == None, mainText))
    #mainText = list(filter(lambda x: x != '', mainText))
    #mainText = list(map(lambda x: x.strip(), mainText))
    #mainText = ''.join(mainText)
    return mainText
# Search for News Article & Press
def ArticleInNaver(cat, url):
    articleIdList = ['articeBody', 'newsEndContents', 'articleBodyContents']
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
    try:
        mainText = FilterMainText(webPage.find('div', id=mainTextId))
    except AttributeError:
        articleIdList.remove(mainTextId)
        try:
            mainText = FilterMainText(webPage.find('div', id=articleIdList[0]))
        except AttributeError:
                mainText = FilterMainText(webPage.find('div', id=articleIdList[1]))
        else:pass
    else:pass
    press = webPage.find(class_=pressClass)
    press = press.find('img').attrs['alt']
    return mainText, press
# Search for Comment
def CommentInNaver(cat, url):
    global os
    driver = OS_Driver(os)
    if cat == r'연예':
        commentByClass = 'reply_count';
        commentNumByClass = 'u_cbox_count'
    elif cat == r'스포츠':
        commentByClass = 'comment';
        commentNumByClass = 'u_cbox_count'
    else:
        commentByClass = 'pi_btn_count';
        commentNumByClass = 'u_cbox_count'
    commentMore = 'u_cbox_paginate'
    driver.get(url)
    commentClassList = ['reply_count', 'comment', 'pi_btn_count']
    try:
        element = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, commentByClass)))
        moreCommentPage = driver.find_element_by_class_name(commentByClass)
        webdriver.ActionChains(driver).move_to_element(moreCommentPage).click(moreCommentPage).perform()
    except TimeoutException:
        commentClassList.remove(commentByClass)
        try:
            element = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, commentClassList[0])))
            moreCommentPage = driver.find_element_by_class_name(commentClassList[0])
            webdriver.ActionChains(driver).move_to_element(moreCommentPage).click(moreCommentPage).perform()
        except TimeoutException:
            element = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.CLASS_NAME, commentClassList[1])))
            moreCommentPage = driver.find_element_by_class_name(commentClassList[1])
            webdriver.ActionChains(driver).move_to_element(moreCommentPage).click(moreCommentPage).perform()
        else:pass
    else:pass
    try:
        element = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, commentNumByClass)))
        commentNum = driver.find_element_by_class_name(commentNumByClass).text
        commentNum = ''.join(commentNum.split(','))
    except NoSuchElementException:
        element = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, commentNumByClass)))
        commentNum = driver.find_element_by_class_name(commentNumByClass).text
        commentNum = ''.join(commentNum.split(','))
    except TimeoutException:
        element = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, commentNumByClass)))
        commentNum = driver.find_element_by_class_name(commentNumByClass).text
        commentNum = ''.join(commentNum.split(','))
    else:
        pass
    print('naver Information Number of comment : {}'.format(commentNum))
    print('naver Start : Click More Button')
    loop = True
    while loop == True:
        try:
            element = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.CLASS_NAME, commentMore)))
            moreComment = driver.find_element_by_class_name(commentMore)
        except TimeoutException:
            try:
                element = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, commentMore)))
                moreComment = driver.find_element_by_class_name(commentMore)
                webdriver.ActionChains(driver).move_to_element(moreComment).click(moreComment).perform()
            except NoSuchElementException:
                loop = False
            except TimeoutException:
                loop = False
        except StaleElementReferenceException:
            try:
                element = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, commentMore)))
                moreComment = driver.find_element_by_class_name(commentMore)
                webdriver.ActionChains(driver).move_to_element(moreComment).click(moreComment).perform()
            except StaleElementReferenceException:
                loop = False
            except TimeoutException:
                loop = False
        else:
            webdriver.ActionChains(driver).move_to_element(moreComment).click(moreComment).perform()
            if moreComment.get_attribute('style') != '':
                loop = False
    print('naver End Click More Button & Start Crawling comments')
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    commentsDf = pd.DataFrame({'comments': soup.select('#cbox_module > div > div.u_cbox_content_wrap > ul > li > div.u_cbox_comment_box > div > div.u_cbox_text_wrap > span.u_cbox_contents'),
                               '공감': soup.select('#cbox_module > div > div.u_cbox_content_wrap > ul > li > div.u_cbox_comment_box > div > div.u_cbox_tool > div > a.u_cbox_btn_recomm'),
                               '비공감': soup.select('#cbox_module > div > div.u_cbox_content_wrap > ul > li > div.u_cbox_comment_box > div > div.u_cbox_tool > div > a.u_cbox_btn_unrecomm')
                               })
    driver.quit()
    commentsDf = commentsDf.apply(lambda x: ExtractElementFromRow(x), axis=1)
    print('naver Number of comment : {}'.format(len(commentsDf)))
    print ('naver End')
    return commentsDf, int(commentNum), len(commentsDf)
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
def Main_Naver(runDate, xdaysAgo):
    naverAPI, basePage, targetPage = Resource_Naver()
    targetDate = runDate - timedelta(days = xdaysAgo)
    print('Site : {}, Run Date : {}, Goal Date : {}'.format('Naver', runDate.strftime('%Y.%m.%d'), targetDate.strftime('%Y.%m.%d')))
    pageForTargetDate = SearchDateForNaver(targetDate, basePage, targetPage)
    categoryInRankingNews = CategoryWebPathForNaver(targetDate, basePage, pageForTargetDate)
    outNews = pd.DataFrame()
    outComment = pd.DataFrame()
    for idx in categoryInRankingNews.index:
        data = categoryInRankingNews.loc[idx]
        category = data['category']
        print('{} : {}'.format('Naver',category))
        link = data['link']
        newsList = NewsListInCategoryForNaver(targetDate.strftime('%Y.%m.%d'), basePage, category, link)
        newsList = pd.concat([pd.DataFrame([category] * len(newsList), columns=['category']), newsList], axis=1)
        newsList['press'] = ''
        newsList['mainText'] = ''
        newsList['number_of_comment'] = ''
        newsList['real_number_of_comment'] = ''
        for idx2 in newsList.index:
            newsInfo = ArticleInNaver(category, newsList.loc[idx2]['link'])
            newsList.loc[idx2, 'press'] = newsInfo[1]
            newsList.loc[idx2, 'mainText'] = newsInfo[0]
            print('{} : {}, {}'.format('Naver', idx2, newsList.loc[idx2]['link']))
            comments, commentNum, num_commentDf = CommentInNaver(category, newsList.loc[idx2]['link'])
            newsList.loc[idx2, 'number_of_comment'] = commentNum
            newsList.loc[idx2, 'real_number_of_comment'] = num_commentDf
            baseDf = pd.DataFrame({'category': [newsList.loc[idx2]['category']] * len(comments),
                                   'date': [newsList.loc[idx2]['date']] * len(comments),
                                   'rank': [newsList.loc[idx2]['rank']] * len(comments)})
            commentsList = pd.concat([baseDf, comments], axis=1)
            outComment = pd.concat([outComment, commentsList], axis=0)
        outNews = pd.concat([outNews, newsList], axis=0)
    outNews['site'] = 'Naver'
    outComment['site'] = 'Naver'
    outNews.reset_index(drop = True, inplace = True)
    outComment.reset_index(drop = True, inplace = True)
    return outNews, outComment
# --------------------------------------------------------------------
# Crawling for Daum
# --------------------------------------------------------------------
# Resource for Daum
def Resource_Daum():
    rankPage = 'http://media.daum.net/ranking/popular/?regDate='
    mainPage = 'http://media.daum.net'
    return mainPage, rankPage
# Search for category web path
def CategoryWebPathForDaum(mainPage, url):
    soup = WebPageUsingBS(url, 'xml')
    targetList = soup.select('#mArticle > div.rank_news > ul.tab_sub > li > a')[1:]
    outDf = pd.DataFrame(list(map(lambda x: SearchTargetForDaum(x, mainPage), targetList)))
    return outDf
# Search for category web path
def SearchTargetForDaum(target, mainPage):
    category = target.text.strip()
    link = mainPage + target.attrs['href']
    return {'category': category, 'link' : link}
# Search for news list in category
def NewsListInCategoryForDaum(date, cat, url):
    soup = WebPageUsingBS(url, 'html')
    newsList = soup.select('#mArticle > div.rank_news > ul.list_news2 > li')
    dp = pd.DataFrame(list(map(lambda x: NewsDataForDaum(date, cat, x), newsList)))
    return dp
# Search for news information
def NewsDataForDaum(date, cat, source):
    rank = source.find('span', class_='screen_out').text
    press = source.find('span', class_='info_news').text
    title = source.find('a', class_='link_txt').text
    link = source.find('a', class_='link_txt').attrs['href']
    return {'category':cat, 'date':date, 'rank':rank, 'press':press, 'title':title, 'link':link}
# Search for comment in news
def CommentsInDaum(df):
    recomm =  df['comments'].find('span', class_='comment_recomm')
    recomm = list(map(lambda x: x.text, recomm.find_all('button')))
    recomm = list(map(lambda x: re.search('[\d]+', x).group(), recomm))
    df[r'공감'] = recomm[0]
    df[r'비공감'] = recomm[1]
    if df['comments'].find('p').text == '':
        comments = '이미지 또는 특수문자입니다. '
    else:
        comments = '\s'.join(df['comments'].find('p').text.split('\n'))
    df['comments'] = comments
    return df
# Check Whether element is
def isElementPresent(driver, locator):
    try:
        driver.find_element_by_class_name(locator)
    except NoSuchElementException:
        return False
    return True
# Search for article in news
def NewsArticleForDaum(cat, url):
    global os
    driver = OS_Driver(os)
    driver.get(url)
    print('daum Start : Search Main Text')
    element = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, 'article_view')))
    article = driver.find_element_by_class_name('article_view')
    article = article.find_elements_by_tag_name('p')
    article = '\s'.join(list(map(lambda x: x.text.strip(), article)))
    print('daum End : Search Main Text')
    print('daum Start : Search Keywords')
    if isElementPresent(driver, 'tag_relate') == False:
        keywords = 'NaN'
    else:
        element = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.CLASS_NAME, 'tag_relate')))
        keywords = driver.find_elements_by_class_name('tag_relate')
        keywords = list(map(lambda x: x.text, keywords))
        keywords = list(map(lambda x: re.sub('#', '', x), keywords))
    print('daum End : Search Keywords')
    element = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.CLASS_NAME, 'num_count')))
    numComment = int(driver.find_element_by_class_name('num_count').text)
    print('daum information Number of comment : {}'.format(numComment))
    print('daum Start : Click More Button & Crawling comment')
    try:
        element = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.ID, 'alex-area')))
    except:
        pass
    else:
        loop = True
        more_button_position = 0
        more_button_position_count = 10
        while loop:
            try:
                commentsByclass = 'alex_more'
                element = WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((By.CLASS_NAME, commentsByclass)))
                more_button = driver.find_element_by_class_name(commentsByclass)
                webdriver.ActionChains(driver).move_to_element(more_button).click(more_button).perform()
                commentElements = driver.find_elements_by_class_name('cmt_info')
                more_button.is_displayed()
            except:
                try:
                    element = WebDriverWait(driver, 1.5).until(
                        EC.presence_of_element_located((By.CLASS_NAME, commentsByclass)))
                except NoSuchElementException:
                    loop = False
                except StaleElementReferenceException:
                    loop = False
                except TimeoutException:
                    loop = False
                else:
                    pass
            else:
                try:
                    element = WebDriverWait(driver, 1).until(
                        EC.presence_of_element_located((By.CLASS_NAME, commentsByclass)))
                except:
                    try:
                        element = WebDriverWait(driver, 1).until(
                            EC.presence_of_element_located((By.CLASS_NAME, commentsByclass)))
                    except NoSuchElementException:
                        loop = False
                    except StaleElementReferenceException:
                        loop = False
                    except TimeoutException:
                        loop = False
                    else:
                        pass
                else:
                    try:
                        more_button.is_displayed()
                    except StaleElementReferenceException:
                        loop = False
                    except NoSuchElementException:
                        loop = False
                    else:
                        if more_button_position == more_button.location['y']:
                            if len(commentElements) / numComment >= 0.5:
                                more_button_position_count -= 1
                            else:
                                more_button_position_count -= 0.25
                        more_button_position = more_button.location['y']
                        if more_button_position_count <= 0:
                            loop = False
        try:
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            comment_Df = soup.select('#alex-area > div > div > div > div.cmt_box > ul.list_comment > li')
            comment_Df = pd.DataFrame(comment_Df)
            comment_Df.rename({0:'comments'}, axis = 1,inplace = True)
            comment_Df = comment_Df.apply(lambda x: CommentsInDaum(x), axis = 1)
        except AttributeError:
            driver.implicitly_wait(1)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            comment_Df = soup.select('#alex-area > div > div > div > div.cmt_box > ul.list_comment > li')
            comment_Df = pd.DataFrame(comment_Df)
            comment_Df.rename({0: 'comments'}, axis=1, inplace=True)
            comment_Df = comment_Df.apply(lambda x: CommentsInDaum(x), axis=1)
        else:
            driver.quit()

        print('daum End : Click More Button & Crawling comment')
        print('daum Number of comment : {}'.format(len(comment_Df)))
        print ('daum End')
    return keywords, article, comment_Df, int(numComment), len(comment_Df)
# Run in Daum
def Main_Daum(runDate, xdaysAgo):
    print('{}'.format('Daum'))
    mainPage, rankPage = Resource_Daum()
    targetDate = runDate - timedelta(days=xdaysAgo)
    linkForCategory = CategoryWebPathForDaum(mainPage, rankPage+targetDate.strftime('%Y%m%d'))
    print('Site : {}, Run Date : {}, Goal Date : {}'.format('Daum', runDate.strftime('%Y.%m.%d'),
                                                            targetDate.strftime('%Y.%m.%d')))
    targetDate = targetDate.strftime('%Y.%m.%d')
    outNews = pd.DataFrame()
    outComment = pd.DataFrame()
    for idx in linkForCategory.index:
        data = linkForCategory.loc[idx]
        category = data['category']
        print('{} : {}'.format('Daum', category))
        link = data['link']
        newsList = NewsListInCategoryForDaum(targetDate, category, link)
        newsList['mainText'] = ''
        newsList['keywords'] = ''
        newsList['number_of_comment'] = ''
        newsList['real_number_of_comment'] = ''
        for idx2 in newsList.index:
            newsLink = newsList.loc[idx2]['link']
            print('{} : {}, {}'.format('Daum', idx2, newsLink))
            keywords, article, comments, numComment, num_comment_Df= NewsArticleForDaum(category, newsLink)
            newsList.loc[idx2, 'keywords'] = keywords
            newsList.loc[idx2, 'mainText'] = article
            newsList.loc[idx2, 'number_of_comment'] = numComment
            newsList.loc[idx2, 'real_number_of_comment'] = num_comment_Df
            baseDf = pd.DataFrame({ 'category' : [newsList.loc[idx2]['category']] * len(comments),
                                  'date' : [newsList.loc[idx2]['date']] * len(comments),
                                  'rank' : [newsList.loc[idx2]['rank']] * len(comments)}
                                  )
            commentsList = pd.concat([baseDf, comments], axis = 1)
            outComment = pd.concat([outComment, commentsList], axis = 0)
        outNews = pd.concat([outNews, newsList], axis = 0)
    outNews['site'] = 'daum'
    outComment['site'] = 'daum'
    outNews.reset_index(drop=True, inplace=True)
    outComment.reset_index(drop=True, inplace=True)
    return outNews, outComment
def Main(site,db_name, runDate, xdaysAgo):
    mongodb = dh.ToMongoDB(*dh.AWS_MongoDB_Information())
    dbname = db_name
    useDb = dh.Use_Database(mongodb, dbname)
    slack = cb.Slacker(cb.slacktoken())
    startTime = datetime.now()
    if site.lower() == 'naver':
        newsDf, commentsDf = Main_Naver(runDate, xdaysAgo)
        newsCollectionName = 'newsNaver'
    elif site.lower() == 'daum':
        newsDf, commentsDf = Main_Daum(runDate, xdaysAgo)
        newsCollectionName = 'newsDaum'
    else:
        raise NotMatch('Not Match site')
    middleTime = datetime.now()
    runningTime = middleTime = middleTime - startTime
    print ('Start Uploading')
    useCollection_daum_news = dh.Use_Collection(useDb, newsCollectionName)
    useCollection_daum_news.insert_many(newsDf.to_dict('records'))
    useCollection_comment = dh.Use_Collection(useDb, 'comments')
    useCollection_comment.insert_many(commentsDf.to_dict('records'))
    print ('End Uploading')
    endTime = datetime.now()
    uploadTime = endTime - middleTime
    targetDate = runDate - timedelta(days=xdaysAgo)
    outcome_info = '{}, news : {}, comment : {}'.format(site, len(newsDf), len(commentsDf))
    date_info = 'run date : {}, target date : {}'.format(runDate.strftime('%Y%m%d'), targetDate.strftime('%Y%m%d'))
    time_info = 'running time : {}, uploading time'.format(runningTime, uploadTime)
    slack.chat.post_message('# general', outcome_info)
    slack.chat.post_message('# general', date_info)
    slack.chat.post_message('# general', time_info)
    slack.chat.post_message('# general', 'Complete Upload In AWS Mongodb')
    mongodb.close()
os = 'windows'
if __name__ == "__main__":
    site = sys.argv[1]
    xdaysAgo = sys.argv[2]
    #site = 'daum'
    #xdaysAgo = '5'
    xdaysAgo = int(xdaysAgo)
    runDate = datetime.now().date()
    Main(site, 'hy_db', runDate, xdaysAgo)
