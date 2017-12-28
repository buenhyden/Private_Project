import pandas as pd
import itertools
import sys
from glob import glob
import re
def Read_File(file):
    df = pd.read_csv(file,encoding = 'utf-8', engine = 'python')
    targetColumns = list(filter(lambda x: ('인물' in x) or ('기관' in x) or ('지역' in x) or ('장소' in x),df.columns.values))
    if len(targetColumns) != 0:
        return df[targetColumns]
    else:
        return df[targetColumns]
def Filter1(isList):
    tmp1 = set(isList)
    tmp1 = list(filter(lambda x: type(x)!=float, tmp1))
    tmp2 = list(map(lambda x: x.split(','), tmp1))
    tmp3 = set(map(lambda x: x.strip(), set(itertools.chain.from_iterable(tmp2))))
    tmp3 = list(filter(lambda x: len(x)>1, tmp3))
    tmp3 = list(filter(lambda x: x!='', tmp3))
    tmp3 = list(map(lambda x: x.strip(), tmp3))
    return tmp3
def Extract_Specific_Noun(path):
    fileList = glob(path+'*.csv')
    fileList.extend(glob(path+'CSV'))
    outDf = pd.DataFrame()
    for file in fileList:
        data = Read_File(file)
        if len(outDf) == 0:
            outDf = data
        else:
            outDf = pd.concat([outDf, data], axis = 0)
    outDf.reset_index(drop=True, inplace=True)
    outDf.astype(str)
    outDf = outDf.to_dict('list')
    outDict = dict()
    for outKey in outDf:
        outDict[outKey] = Filter1(outDf[outKey])
    return outDict

def MakeCombination(li):
    outlist = []
    for ix in range(1, len(li)+1):
        outlist += list(itertools.permutations(li,ix))
    outlist = list(map(lambda x: ' '.join(x), outlist)) + list(map(lambda x: ''.join(x), outlist))
    outlist = list(filter(lambda x: len(x)!=1, outlist))
    outlist = outlist + list(map(lambda x: re.sub('[\W]','', x), outlist))
    return outlist
def filter2(idx):
    idx2 = set(filter(lambda x: x!='', set(MakeCombination(idx.split(' ')))))
    idx2 = set(filter(lambda x: not '  'in x , idx2))
    idx2 = set(map(lambda x: x.strip(), idx2))
    return idx2
def Read_File2(file):
    df = pd.read_csv(file,encoding = 'utf-8', engine = 'python')
    targetColumns = list(filter(lambda x: x in ['중요키워드','키워드','keword','토픽키워드','토픽 키워드'], df.columns.values))
    if len(targetColumns) != 0:
        return df[targetColumns]
    else:
        return df[targetColumns]
def Extract_Keywords(path):
    fileList = glob(path+'*.csv')
    fileList.extend(glob(path+'*.CSV'))
    outDf = pd.DataFrame()
    for file in fileList:
        df = Read_File2(file)
        if len(outDf) == 0:
            outDf = df
        else:
            outDf = pd.concat([outDf, df], axis = 0)
    outDf.reset_index(drop=True, inplace = True)
    outDf.astype(str)
    outDf = outDf.to_dict('list')
    outDict = dict()
    for outKey in outDf:
        outDict[outKey] = filter3(outDf[outKey])
    return outDict
def filter3(isList):
    tmp1 = set(isList)
    tmp1 = list(filter(lambda x: type(x)!=float, tmp1))
    tmp2 = list(map(lambda x: x.split(','), tmp1))
    tmp3 = set(map(lambda x: x.strip(), set(itertools.chain.from_iterable(tmp2))))
    tmp3 = list(filter(lambda x: len(x)>1, tmp3))
    tmp3 = list(filter(lambda x: x!='', tmp3))
    tmp3 = list(map(lambda x: x.strip(), tmp3))
    return tmp3
if __name__ == '__main__':
    path1 = './data/news/high_frequency_noun/'
    path2 = './data/news/mainissue/'
    path3 = './data/news/newstopic/'
    path4 = './data/news/people/'
    path5 = './data/news/4th_industry/'
    path6 = './data/news/have_negative_positive/constitution/'
    path7 = './data/news/have_negative_positive/household_debt/'
    path8 = './data/news/have_negative_positive/olymphic/'
    path9 = './data/news/have_negative_positive/'
    path10 = './data/news/etc1/'
    path11 = './data/news/etc2/'
    titleDf = pd.read_csv('./data/title_from_wiki_and_namuwiki.txt', encoding='utf-8', header=None)
    if int(sys.argv[1])==1:
        print (1)
        pathList2 = [path4, path5, path6, path7, path8, path9, path10, path11]
        outpath = './data/news/'
        for path in pathList2:
            esn = Extract_Specific_Noun(path)
            basename = path.split('/')[-2]
            outfilename1 = outpath + 'noun_from_news_bigdata_' + basename + '_include_wiki_keywords.txt'
            outfilename2 = outpath + 'noun_from_news_bigdata_' + basename + '_exclude_wiki_keywords.txt'
            outSet = set()
            for info in esn:
                out = pd.DataFrame(esn[info])
                out = out[out[0].str.match('[a-zA-Z0-9가-힣\s]+$')]
                out.reset_index(drop=True, inplace=True)
                out = out[0].apply(lambda x: filter2(x))
                out.apply(lambda x: outSet.update(x))
            pdf = pd.DataFrame(list(outSet))
            pdf[pdf[0].isin(titleDf[0])].to_csv(outfilename1, index=False, header=False, encoding='utf-8')
            pdf[~pdf[0].isin(titleDf[0])].to_csv(outfilename2, index=False, header=False, encoding='utf-8')
    else:
        print (2)
        outpath = './data/news/'
        pathList1 = [path1, path2, path3, path4, path5, path6, path7, path8, path9, path10, path11]
        for path1 in pathList1:
            ek = Extract_Keywords(path1)
            basename = path1.split('/')[-2]
            outfilename_1 = outpath + 'keywords_from_news_bigdata_' + basename + '_include_wiki_keywords.txt'
            outfilename_2 = outpath + 'keywords_from_news_bigdata_' + basename + '_exclude_wiki_keywords.txt'
            outSet2 = set()
            for info2 in ek:
                out2 = pd.DataFrame(ek[info2])
                out2 = out2[out2[0].str.match('[a-zA-Z0-9가-힣\s]+$')]
                out2.reset_index(drop=True, inplace=True)
                out2 = out2[0].apply(lambda x: filter2(x))
                out2.apply(lambda x: outSet2.update(x))
            pdf2 = pd.DataFrame(list(outSet2))
            pdf2[pdf2[0].isin(titleDf[0])].to_csv(outfilename_1, index=False, header=False, encoding='utf-8')
            pdf2[~pdf2[0].isin(titleDf[0])].to_csv(outfilename_2, index=False, header=False, encoding='utf-8')