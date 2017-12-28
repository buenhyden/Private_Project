import json
import sys
#filename = '/Users/hyunyoun/Documents/GitHub/Private_Project/personal_project/data/wikidumps/namuwiki_20170327.json'
#filename = '/Users/hyunyoun/Documents/GitHub/Private_Project/personal_project/data/wikidumps'
filename = sys.argv[1]
with open(filename,'r') as data_file:
    data = json.load(data_file )
    data_file.close()
with open('./data/out_namu_wiki.txt','w') as f:
    for article in data:
        #print (article)
        #article= article.encode('utf-8')
        #print (article)
        if u'title' in article.keys():
            f.write(article['title'].encode('utf-8')+'\n')