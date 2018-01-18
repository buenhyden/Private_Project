import json
import sys
#filename = '/Users/hyunyoun/Documents/GitHub/Private_Project/personal_project/data/wikidumps/namuwiki_20170327.json'
#filename = '/Users/hyunyoun/Documents/GitHub/Private_Project/personal_project/data/wikidumps'
filename = 'C:/Users/pc/Documents/GitHub/Private_Project/personal_project/data/wikidumps/namuwiki_20170327.json'
with open(filename,'r',encoding='utf-8') as data_file:
    data = json.load(data_file )
    data_file.close()
with open('./data/out_namu_wiki2.txt','w',encoding='utf-8') as f:
    for article in data:
        #print (article)
        #article= article.encode('utf-8')
        #print (article)
        if 'title' in article.keys():
            f.write(article['title']+'\n')