# coding: utf-8


import pickle
import sys
from datetime import datetime
from multiprocessing import cpu_count

import pandas as pd
import dask.dataframe as dd

import Database_Handler as dh
import Basic_Module as bm

if sys.argv[1] == 'naver':
    # Naver
    data = pickle.load(open('./data/pre_data/stastics/for_statistics_Naver_from_mongodb.pickled', 'rb'))
    data = pd.DataFrame.from_dict(data, orient='index')
    data.reset_index(inplace=True)
    data.rename(columns={'index': 'id'}, inplace=True)
    print('Naver : {}'.format(data.shape))
    extData = data.loc[:, ['id', 'title', 'date', 'press', 'rank', 'category', 'number_of_comment',
                           'number_of_crawled_comment']].copy()
    extData['site'] = pd.Series(['Naver'] * extData.shape[0])

else:
    # Daum
    data = pickle.load(open('./data/pre_data/stastics/for_statistics_daum_from_mongodb.pickled', 'rb'))
    data = pd.DataFrame.from_dict(data, orient='index')
    data.reset_index(inplace=True)
    data.rename(columns={'index': 'id'}, inplace=True)
    print('Daum : {}'.format(data.shape))
    extData = data.loc[:, ['id', 'title', 'date', 'press', 'rank', 'category', 'number_of_comment',
                           'number_of_crawled_comment']].copy()
    extData['site'] = pd.Series(['daum'] * extData.shape[0])


def GetNumberOfCommentInDB(row):
    import Database_Handler as dh
    from bson import ObjectId
    mongodb = dh.ToMongoDB(*dh.GCP_MongoDB_Information())
    dbname = 'hy_db'
    useDB = dh.Use_Database(mongodb, dbname)
    commentCollection = dh.Use_Collection(useDB, 'comments')
    info = {'site': row['site'],
            'category': row['category'],
            'date': row['date'],
            'rank': row['rank']}
    commentsForNews = commentCollection.find(info)
    realNumCount = commentsForNews.count()
    site = row['site']
    oid = ObjectId(row['id'])
    if site == 'daum':
        newsCollection = dh.Use_Collection(useDB, 'newsDaum')
    else:
        newsCollection = dh.Use_Collection(useDB, 'newsNaver')
    if realNumCount != row['number_of_crawled_comment']:
        newsCollection.update_one({'_id': oid},
                                  {'$set': {'real_number_of_comment': realNumCount}})
    if row.name % 100 == 0:
        print(row.name)


if __name__ == "__main__":
    start = datetime.now()
    ddf = dd.from_pandas(extData, npartitions=cpu_count())
    ddf.apply(GetNumberOfCommentInDB, axis=1, meta = int).compute()
    end = datetime.now()
    print('running time : {}'.format(end - start))