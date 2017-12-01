
# Search for Comments in Entertain News
def CommentsInEntertain(url):
    driver = WebDriver(url)
    element = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, 'u_cbox_in_view_comment')))
    print('Searching more comment point')
    numComment = driver.find_element_by_class_name('u_cbox_count').text
    commentButton = driver.find_element_by_class_name('u_cbox_in_view_comment')
    webdriver.ActionChains(driver).move_to_element(commentButton).click(commentButton).perform()
    print('Number of comment : {}'.format(numComment))
    time.sleep(1)
    print('Start : Search Sort Favorite Button')
    sortButton = '#cbox_module > div > div.u_cbox_sort > div.u_cbox_sort_option > div > ul > li > a'
    element = WebDriverWait(driver, 3).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, sortButton)))
    sortButtons = driver.find_elements_by_css_selector(sortButton)
    favoriteButton = list(filter(lambda xx: xx.get_attribute('data-param') == 'favorite', sortButtons))[0]
    favoriteButton.click()
    print('End : Search Sort Favorite Button')
    time.sleep(1)
    loop = True
    print('Start : Click More Button')
    while loop == True:
        try:
            element = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'u_cbox_paginate')))
            moreComment = driver.find_element_by_class_name('u_cbox_paginate')
            webdriver.ActionChains(driver).move_to_element(moreComment).click(moreComment).perform()
            time.sleep(0.5)
            if moreComment.get_attribute('style') != '':
                loop = False
        except:
            loop = False
    print('End : Click More Button')
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()
    commentsList = soup.find_all(class_='u_cbox_area')
    # commentsList = driver.find_elements_by_xpath('//*[@id="cbox_module"]/div/div[8]/ul/li/div/div')
    outDict = dict()
    print('Number of comment : {}'.format(len(commentsList)))
    print('Start : Crawling comment')
    dp = pd.DataFrame(columns=['comment', '공감', '비공감'])
    for comment in enumerate(commentsList):
        try:
            commentText = comment[1].find(class_='u_cbox_contents').text
            recomm = comment[1].find(class_='u_cbox_btn_recomm')
            recomm = recomm.select_one('em').text
            unrecomm = comment[1].find(class_='u_cbox_btn_unrecomm')
            unrecomm = unrecomm.select_one('em').text
        except:
            pass
        else:
            outDict[comment[0]] = dict()
            dp.loc[len(dp)] = {'comment': commentText, '공감': recomm, '비공감': unrecomm}
    print('End : Crawling comment')
    return dp


# Search for Comments in Sports
def CommentsInSports(url):
    driver = WebDriver(url)
    element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'u_cbox_in_view_comment')))
    print('Searching more comment point')
    numComment = driver.find_element_by_class_name('u_cbox_count').text
    commentButton = driver.find_element_by_class_name('u_cbox_in_view_comment')
    webdriver.ActionChains(driver).move_to_element(commentButton).click(commentButton).perform()
    print('Number of comment : {}'.format(numComment))
    time.sleep(1)
    print('Start : Search Sort Favorite Button')
    sortButton = '#cbox_module > div > div.u_cbox_sort > div.u_cbox_sort_option > div > ul > li > a'
    element = WebDriverWait(driver, 3).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, sortButton)))
    sortButtons = driver.find_elements_by_css_selector(sortButton)
    favoriteButton = list(filter(lambda xx: xx.get_attribute('data-param') == 'like', sortButtons))[0]
    favoriteButton.click()
    print('End : Search Sort Favorite Button')
    time.sleep(0.5)
    loop = True
    print('Start : Click More Button')
    while loop == True:
        try:
            element = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'u_cbox_paginate')))
            moreComment = driver.find_element_by_class_name('u_cbox_paginate')
            webdriver.ActionChains(driver).move_to_element(moreComment).click(moreComment).perform()
            time.sleep(0.5)
            if moreComment.get_attribute('style') != '':
                loop = False
        except:
            loop = False
    print('End : Click More Button')
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()
    commentsList = soup.find_all(class_='u_cbox_area')
    # commentsList = driver.find_elements_by_xpath('//*[@id="cbox_module"]/div/div[8]/ul/li/div/div')
    outDict = dict()
    print('Number of comment : {}'.format(len(commentsList)))
    print('Start : Crawling comment')
    dp = pd.DataFrame(columns=['comment', '공감', '비공감'])
    for comment in enumerate(commentsList):
        try:
            commentText = comment[1].find(class_='u_cbox_contents').text
            recomm = comment[1].find(class_='u_cbox_btn_recomm')
            recomm = recomm.select_one('em').text
            unrecomm = comment[1].find(class_='u_cbox_btn_unrecomm')
            unrecomm = unrecomm.select_one('em').text
        except:
            pass
        else:
            outDict[comment[0]] = dict()
            dp.loc[len(dp)] = {'comment': commentText, '공감': recomm, '비공감': unrecomm}
    print('End : Crawling comment')
    return dp


# Search for Comments
def Comments(url):
    driver = WebDriver(url)
    element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'u_cbox_btn_view_comment')))
    print('Searching more comment point')
    numComment = driver.find_element_by_class_name('u_cbox_info_txt').text
    commentButton = driver.find_element_by_class_name('u_cbox_btn_view_comment')
    webdriver.ActionChains(driver).move_to_element(commentButton).click(commentButton).perform()
    print('Number of comment : {}'.format(numComment))
    time.sleep(1)
    print('Start : Search Sort Favorite Button')
    sortButton = '#cbox_module > div > div.u_cbox_sort > div.u_cbox_sort_option > div > ul > li > a'
    element = WebDriverWait(driver, 3).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, sortButton)))
    sortButtons = driver.find_elements_by_css_selector(sortButton)
    favoriteButton = list(filter(lambda xx: xx.get_attribute('data-param') == 'favorite', sortButtons))[0]
    favoriteButton.click()
    print('End : Search Sort Favorite Button')
    time.sleep(1)
    loop = True
    print('Start : Click More Button')
    while loop == True:
        try:
            element = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'u_cbox_paginate')))
            moreComment = driver.find_element_by_class_name('u_cbox_paginate')
            webdriver.ActionChains(driver).move_to_element(moreComment).click(moreComment).perform()
            if moreComment.get_attribute('style') != '':
                loop = False
        except:
            loop = False
    print('End : Click More Button')
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()
    commentsList = soup.find_all(class_='u_cbox_area')
    # commentsList = driver.find_elements_by_xpath('//*[@id="cbox_module"]/div/div[8]/ul/li/div/div')
    outDict = dict()
    print('Number of comment : {}'.format(len(commentsList)))
    print('Start : Crawling comment')
    dp = pd.DataFrame(columns=['comment', '공감', '비공감'])
    for comment in enumerate(commentsList):
        try:
            commentText = comment[1].find(class_='u_cbox_contents').text
            recomm = comment[1].find(class_='u_cbox_btn_recomm')
            recomm = recomm.select_one('em').text
            unrecomm = comment[1].find(class_='u_cbox_btn_unrecomm')
            unrecomm = unrecomm.select_one('em').text
        except:
            pass
        else:
            outDict[comment[0]] = dict()
            dp.loc[len(dp)] = {'comment': commentText, '공감': recomm, '비공감': unrecomm}
    print('End : Crawling comment')
    return dp


# Run in Naver
def Main_Naver():
    print('{}'.format('Naver'))
    resource = Resource_Naver()
    dateInfo = SearchDateForNaver(resource[1], resource[2])
    category = CategoryWebPathForNaver(resource[1], dateInfo[1])
    outNews = pd.DataFrame()
    outComment = pd.DataFrame()
    print(dateInfo)
    for cat in category:
        link = category[cat]
        print(cat)
        if cat == r'스포츠':
            newsList = NewsListInCategorySportsForNaver(dateInfo[0], cat, link)
        elif cat == r'연예':
            newsList = NewsListInCategoryEntertaInForNaver(dateInfo[0], cat, link)
        else:
            newsList = NewsListInCategoryForNaver(dateInfo[0], resource[1], cat, link)
        newsList['press'] = ''
        newsList = pd.concat([pd.DataFrame([cat] * len(newsList), columns=['category']), newsList], axis=1)
        newsList['mainText'] = ''
        for idx in newsList.index:
            print(idx, )
            newsLink = newsList.loc[idx]['link']
            if cat == r'연예':
                articleText = ArticleInEntertain(newsLink)
            elif cat == r'스포츠':
                articleText = ArticleInSports(newsLink)
            else:
                articleText = Article(newsLink)
            newsList.loc[idx]['mainText'] = articleText[0]
            newsList.loc[idx]['press'] = articleText[1]
            if cat == r'스포츠':
                comments = CommentsInSports(newsLink)
            elif cat == r'연예':
                comments = CommentsInEntertain(newsLink)
            else:
                comments = Comments(newsLink)
            baseDf = pd.DataFrame({'category': [newsList.loc[idx]['category']] * len(comments),
                                   'date': [newsList.loc[idx]['date']] * len(comments),
                                   'rank': [newsList.loc[idx]['rank']] * len(comments)})
            commentsList = pd.concat([baseDf, comments], axis=1)
            outNews = pd.concat([outNews, newsList], axis=0)
            outComment = pd.concat([outComment, commentsList], axis=0)
        break
    return outNews, outComment


# --------------------------------------------------------------------
# Crawling for Daum
# --------------------------------------------------------------------
# Resource for Daum
def Resource_Daum():
    newPage = 'http://media.daum.net/ranking/popular/'
    mainPage = 'http://media.daum.net'
    runDate = datetime.now()
    return mainPage, newPage, runDate


# Search for news ranking
def SearchRanking(url):
    soup = WebPage(url, 'lxml')
    date = soup.find(class_='box_calendar')
    todayIs = date.find(class_='screen_out').text
    compileIs = re.compile('[\d]+')
    todayIs = '.'.join(compileIs.findall(todayIs))
    yesterdayIs = soup.select_one('a.btn_date.btn_prev').attrs['href']
    return todayIs, yesterdayIs


# Search for category web path
def PopularPage(mainPage, url):
    link = mainPage + url
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
        outDict[category] = mainPage + link
    return targetDate, outDict


# Search for news list in category
def NewsListInCategoryInDaum(date, cat, url):
    soup = WebPage(url, 'html.parser')
    newsList = soup.select('#mArticle > div.rank_news > ul.list_news2 > li')
    outdict = dict()
    dp = pd.DataFrame(columns=['category', 'date', 'rank', 'title', 'link', 'press'])
    for news in newsList:
        x = NewsData(date, cat, news)
        dp.loc[len(dp)] = x
    return dp


# Search for news information
def NewsData(date, cat, source):
    rank = source.find('span', class_='screen_out').text
    press = source.find('span', class_='info_news').text
    title = source.find('a', class_='link_txt').text
    link = source.find('a', class_='link_txt').attrs['href']
    return {'category': cat, 'date': date, 'rank': rank, 'press': press, 'title': title, 'link': link}


# Search for comment in news
def CommentsInDaum(ss):
    comments = ss.find_element_by_tag_name('p').text
    recomm = ss.find_element_by_class_name('comment_recomm')
    like = recomm.find_element_by_xpath('button[1]').text
    dislike = recomm.find_element_by_xpath('button[2]').text
    like = (r'공감', like.split('\n')[1])
    dislike = (r'비공감', dislike.split('\n')[1])
    return dict([('comment', comments), like, dislike])


# Search for article in news
def NewsArticle(url):
    #chromedriver = '/Users/hyunyoun/Programming/chromedriver'
    #driver = webdriver.Chrome(chromedriver)
    #driver.get(url)
    driver = WebDriver(url)
    print('Start : Search Main Text')
    article = driver.find_element_by_class_name('news_view').text
    print('End : Search Main Text')
    print('Start : Search Keywords')
    keywords = driver.find_elements_by_css_selector(
        '#mArticle > div.foot_view > div.relate_tag.hc_news_pc_mArticle_relatedTags > span > a > span')
    keywords = list(map(lambda x: x.text, keywords))
    keywords = list(filter(lambda x: re.sub('#', '', x), keywords))
    print('End : Search Keywords')
    print('Start : Search Sort Favorite Button')
    recomm = '//*[@id="alex-area"]/div/div/div/div[3]/ul[1]/li[1]/button'
    element = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, recomm)))
    element.click()
    print('End : Search Sort Favorite Button')
    numComment = driver.find_element_by_class_name('num_count').text
    print('Number of comment : {}'.format(numComment))
    print('Start : Click More Button & Crawling comment')
    try:
        element = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.ID, 'alex-area')))
    except:
        pass
    else:
        loop = True
        driver.save_screenshot('screen1.png')
        driver.set_page_load_timeout(5)
        while loop:
            try:
                className = 'alex_more'
                element = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, className)))

                more_button = driver.find_element_by_class_name(className)
                webdriver.ActionChains(driver).move_to_element(more_button).click(more_button).perform()
                # webdriver.ActionChains(driver).click(more_button).perform()
                driver.save_screenshot('screen2.png')
            except TimeoutException:
                loop = False
            except NoSuchElementException:
                try:
                    element = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, className)))
                    more_button.is_displayed()
                except StaleElementReferenceException:
                    loop = False
                else:
                    pass
            except StaleElementReferenceException:
                loop = False
            driver.save_screenshot('screen3.png')
        cSS2 = "#alex-area > div > div > div > div.cmt_box > ul.list_comment"
        comment_box = driver.find_element_by_css_selector(cSS2)
        comment_list = comment_box.find_elements_by_tag_name("li")
        print(len(comment_list))
        comment_list = list(map(lambda x: CommentsInDaum(x), comment_list))
        print('End : Click More Button & Crawling comment')
        print('Number of comment : {}'.format(len(comment_list)))
        print('End : Crawling comment')
    driver.quit()
    comment_list = pd.DataFrame(comment_list)
    return keywords, article, comment_list


# Run in Daum
def Main_Daum():
    print('{}'.format('Daum'))
    resourceDaum = Resource_Daum()
    first = SearchRanking(resourceDaum[1])
    second = PopularPage(resourceDaum[0], first[1])
    outNews = pd.DataFrame()
    outComment = pd.DataFrame()
    print(second[0])
    for category in second[1]:
        print(category)
        newsList = NewsListInCategoryInDaum(second[0], category, second[1][category])
        newsList['mainText'] = ''
        newsList['keywords'] = ''
        for news in newsList.index:
            print(news, )
            articleInfo = NewsArticle(newsList.loc[news]['link'])
            newsList.loc[news]['mainText'] = articleInfo[1]
            newsList.loc[news]['keywords'] = ','.join(articleInfo[0])
            baseDf = pd.DataFrame({'category': [newsList.loc[news]['category']] * len(articleInfo[2]),
                                   'date': [newsList.loc[news]['date']] * len(articleInfo[2]),
                                   'rank': [newsList.loc[news]['rank']] * len(articleInfo[2])})
            comments = pd.concat([baseDf, articleInfo[2]], axis=1)
            outComment = pd.concat([outComment, comments], axis=0)
            break
        outNews = pd.concat([outNews, newsList], axis=0)
        break
    outComment.reset_index(drop=True, inplace=True)
    return outNews, outComment

if __name__ == "__main__":
    # a = Main_Naver()
    b = Main_Daum()