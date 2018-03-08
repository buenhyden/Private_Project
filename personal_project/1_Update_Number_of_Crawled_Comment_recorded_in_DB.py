# coding: utf-8


import pickle
import sys
from datetime import datetime

import pandas as pd
import dask.dataframe as dd

import Database_Handler as dh
import Basic_Module as bm


def GetNumberOfCommentInDB(row):
    import Database_Handler as dh
    mongodb = dh.ToMongoDB(*dh.AWS_MongoDB_Information())
    #mongodb = dh.ToMongoDB(*dh.LOCALHOST_MongoDB_Information())
    dbname = 'hy_db'
    useDB = dh.Use_Database(mongodb, dbname)
    useCollection = dh.Use_Collection(useDB, 'comments')
    info = {'site' : row['site'],
           'category' : row['category'],
           'date' : row['date'],
           'rank' : int(row['rank'])}
    commentsForNews = useCollection.find(info)
    realNumCount = commentsForNews.count()
    if realNumCount != row['number_of_crawled_comment']:
        useCollection.update_one({'_id' : row['id']},
                                 {'$set' : {'number_of_crawled_comment' : realNumCount}})

if sys.argv[1] == 'naver':
    #Naver
    data = pickle.load(open('./data/pre_data/stastics/for_statistics_Naver_from_mongodb.pickled','rb'))
    data = pd.DataFrame.from_dict(data, orient = 'index')
    data.reset_index(inplace = True)
    data.rename(columns = {'index' : 'id'}, inplace = True)
    print ('Naver : {}'.format(data.shape))
    extData = data.loc[:, ['id', 'title', 'date', 'press', 'rank', 'category', 'number_of_comment', 'number_of_crawled_comment']].copy()
    extData['site'] = pd.Series(['Naver']*extData.shape[0])

else:
    #Daum
    data = pickle.load(open('./data/pre_data/stastics/for_statistics_daum_from_mongodb.pickled','rb'))
    data = pd.DataFrame.from_dict(data, orient = 'index')
    data.reset_index(inplace = True)
    data.rename(columns = {'index' : 'id'}, inplace = True)
    print ('Daum : {}'.format(data.shape))
    extData = data.loc[:, ['id', 'title', 'date', 'press', 'rank', 'category', 'number_of_comment', 'number_of_crawled_comment']].copy()
    extData['site'] = pd.Series(['daum']*extData.shape[0])

if __name__ == "__main__":
    start = datetime.now()
    
    extData.apply(GetNumberOfCommentInDB, axis = 1)
    end = datetime.now()
    print ('running time : {}'.format(end - start))

