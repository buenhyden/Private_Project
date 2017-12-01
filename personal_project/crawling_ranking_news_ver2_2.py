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
    '''
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
        '''
        for idx in newsList:
            newsLink = resource[1]+newsList[idx]['link']
            print (newsLink)
            articleText = Article(newsLink)
            print (articleText)
            comments = Comments(newsLink)
        break
    '''