# coding: utf-8
# # Train Classifier For News Classification
# > ## * Word2Vec

def Make_Roc_Curve(x, y, model1, model2, model3, model4):
    import matplotlib.pyplot as plt
    print ('Logistic Regression')
    fpr1, tpr1, thresholds1 = roc_curve(y, model1.predict(x))
    print ('Random Forest')
    fpr2, tpr2, thresholds2 = roc_curve(y, model2.predict(x))
    print ('Kernel SVM')
    fpr3, tpr3, thresholds3 = roc_curve(y, model3.predict(x))
    print ('XGBoost')
    import xgboost as xgb
    fpr4, tpr4, thresholds4 = roc_curve(y, model4.predict(xgb.DMatrix(x)))
    plt.plot(fpr1, tpr1, label="Logistic Regression")
    plt.plot(fpr2, tpr2, label="RandomForest")
    plt.plot(fpr3, tpr3, label="Kernel SVM")
    plt.plot(fpr4, tpr4, label='XGBoost')
    plt.legend()
    plt.plot([0, 1], [0, 1], 'k--', label="random guess")
    plt.xlabel('False Positive Rate (Fall-Out)')
    plt.ylabel('True Positive Rate (Recall)')
    plt.title('Receiver operating characteristic')
    plt.show()

def plot_history(history):
    import matplotlib.pyplot as plt
    """Plot model history after `fit()`.
    """
    # summarize history for accuracy
    plt.plot(history.history['acc'])
    plt.plot(history.history['val_acc'])
    plt.title('model accuracy')
    plt.ylabel('accuracy')
    plt.xlabel('epoch')
    plt.legend(['train', 'valid'], loc='upper left')
    plt.show()

    # summarize history for loss
    plt.plot(history.history['loss'])
    plt.plot(history.history['val_loss'])
    plt.title('model loss')
    plt.ylabel('loss')
    plt.xlabel('epoch')
    plt.legend(['train', 'valid'], loc='upper left')
    plt.show()

def Make_TSNE1(n_component, model, wv, limit):
    from sklearn.manifold import TSNE
    import matplotlib.pyplot as plt
    import pandas as pd
    from tqdm import tqdm
    tqdm.pandas(desc="progress-bar")
    wv = wv[:limit]
    tsne_model = TSNE(n_components=n_component,
                       verbose = 1, random_state = 0)
    tsne_w2v = tsne_model.fit_transform(wv)
    tsne_df = pd.DataFrame(tsne_w2v, columns = ['x', 'y'])
    tsne_df['words'] = list(model.wv.vocab.keys())[:limit]
    i = 0
    for i in tqdm(range(tsne_df['words'].size)):
        plt.scatter(tsne_df['x'][i], tsne_df['y'][i])
        plt.annotate(tsne_df['words'][i], 
                xy = (tsne_df['x'][i], tsne_df['y'][i]))
    plt.show()

def Make_TSNE2(n_component, model, wv, limit):
    from sklearn.manifold import TSNE
    import matplotlib.pyplot as plt
    import pandas as pd
    from tqdm import tqdm
    import bokeh.plotting as bp
    from bokeh.models import HoverTool, BoxSelectTool
    from bokeh.plotting import figure, show, output_notebook
    
    output_notebook()
    plot_tfidf = bp.figure(plot_width=500, plot_height=500, title="A map of word vectors",
    tools="pan,wheel_zoom,box_zoom,reset,hover,previewsave",
    x_axis_type=None, y_axis_type=None, min_border=1)

    word_vectors = [model[w] for w in tqdm(list(model.wv.vocab.keys())[:limit])]

    tsne_model = TSNE(n_components=n_component, verbose=1, random_state=0)
    tsne_w2v = tsne_model.fit_transform(word_vectors)
    # putting everything in a dataframe
    tsne_df = pd.DataFrame(tsne_w2v, columns=['x', 'y'])
    tsne_df['words'] = list(model.wv.vocab.keys())[:limit]

    # plotting. the corresponding word appears when you hover on the data point.
    plot_tfidf.scatter(x='x', y='y', source=tsne_df)
    hover = plot_tfidf.select(dict(type=HoverTool))
    hover.tooltips={"word": "@words"}
    show(plot_tfidf)

def Get_Infer_Vector(docs, model):
    #from tqdm import tqdm
    #tqdm.pandas(desc="progress-bar")
    #return [model.infer_vector(doc.words) for doc in tqdm(docs)]
    return [model.infer_vector(doc.words) for doc in docs]

def Build_tfidf(data):
    from sklearn.feature_extraction.text import TfidfVectorizer
    from tqdm import tqdm
    tqdm.pandas(desc="progress-bar")
    vectorizer = TfidfVectorizer(analyzer = lambda x: x, min_df = 2)
    matrix = vectorizer.fit_transform([x.words for x in tqdm(data)])
    print (matrix.shape)
    tfidf = dict(zip(vectorizer.get_feature_names(), vectorizer.idf_))
    print ('vocab size : {}'.format(len(tfidf)))    
    return tfidf

def buildWordVector(tokens, model, size, tfidf):
    import numpy as np
    vec = np.zeros(size).reshape((1, size))
    count = 0.
    for word in tokens:
        try:
            vec += model[word].reshape((1, size)) * tfidf[word]
            count += 1.
        except KeyError: # handling the case where the token is not
                         # in the corpus. useful for testing.
            continue
    if count != 0:
        vec /= count
    return vec

def Make_Pre_Data(model, tfidf, size, train, test):
    from datetime import datetime
    import numpy as np
    from sklearn.preprocessing import scale
    from tqdm import tqdm
    tqdm.pandas(desc="progress-bar")
    start = datetime.now()
    print (str(model))
    wv = [model[w] for w in tqdm(model.wv.vocab.keys())]
    process1 = datetime.now()
    print ('running time : {}'.format(process1 - start))
    
    print ('Vectorizing Train Data')
    train_vecs_w2v = np.concatenate([buildWordVector(z, model, size, tfidf) for z in tqdm(map(lambda x: x.words, train))])
    print ('scaling Train Data')
    train_vecs_w2v = scale(train_vecs_w2v)
    process2 = datetime.now()
    print ('running time : {}'.format(process2 - process1))
    
    print ('Vectorizing Test Data')
    test_vecs_w2v = np.concatenate([buildWordVector(z, model, size, tfidf) for z in tqdm(map(lambda x: x.words, test))])
    print ('scaling Test Data')
    test_vecs_w2v = scale(test_vecs_w2v)
    process3 = datetime.now()
    print ('running time : {}'.format(process3 - process2))
    
    print ('total running time : {}'.format(process3 - start))
    return wv, train_vecs_w2v, test_vecs_w2v


# In[26]:


def ReMake_Outcome(train_y, test_y):
    from tqdm import tqdm
    import numpy as np
    tqdm.pandas(desc="progress-bar") 
    train_y = np.array([y[0] for y in tqdm(train_y)])
    test_y = np.array([y[0] for y in tqdm(test_y)])
    return train_y, test_y



def Return_ModelName(type, model, tagger):
    size = model.vector_size
    epochs = model.epochs
    window = model.window
    negative = model.negative 
    hs = model.hs 
    sg = model.sg 
    cbow_mean = model.cbow_mean 
    min_count = model.min_count 
    min_alpha = model.min_alpha
    alpha = model.alpha
    modelName = '{}_size-{}_epochs-{}_window-{}_negative-{}_hs-{}_sg-{}_cbow_mean-{}_min_count-{}_min_alpha-{}_alpha-{}_by-{}'.format(
    type, size, epochs, window, negative, hs, sg, cbow_mean, min_count,
    min_alpha, alpha, tagger)
    return modelName


def ConfusionMatrix_To_Heatmap(train_x, train_y, test_x, test_y, classifier, labelEncoder):
    from sklearn.metrics import confusion_matrix
    import matplotlib.pyplot as plt
    import pandas as pd
    import seaborn as sns
    unique_y = list(set(train_y))
    train_confusion = confusion_matrix(train_y, classifier.predict(train_x))
    train_confusion = pd.DataFrame(train_confusion,
                                   columns=labelEncoder.inverse_transform(unique_y),
                                   index=labelEncoder.inverse_transform(unique_y))
    test_confusion = confusion_matrix(test_y, classifier.predict(test_x))
    test_confusion = pd.DataFrame(test_confusion,
                                  columns=labelEncoder.inverse_transform(unique_y),
                                  index=labelEncoder.inverse_transform(unique_y))
    fig = plt.figure(figsize=(16, 6))
    fig.text(0.5, 0.04, 'Predicted', ha='center')
    fig.text(0.04, 0.5, 'Actual', va='center', rotation='vertical')

    ax1 = fig.add_subplot(1, 2, 1)
    plt.title('train data Confusion matrix')
    plt.rcParams['font.family'] = 'NanumBarunGothicOTF'
    sns.heatmap(train_confusion, annot=True, fmt='g', ax=ax1)

    ax2 = fig.add_subplot(1, 2, 2)
    plt.title('test data Confusion matrix')
    plt.rcParams['font.family'] = 'NanumBarunGothicOTF'
    sns.heatmap(test_confusion, annot=True, fmt='g', ax=ax2)


def Roc_Curve_MultiClass(test_x, test_y, classifier, labelEncoder, label):
    from sklearn.preprocessing import label_binarize
    from sklearn.metrics import roc_curve, auc
    import numpy as np
    from scipy import interp
    import matplotlib.pyplot as plt
    from itertools import cycle
    lw = 2
    y_pred = label_binarize(classifier.predict(test_x), classes = label)
    y_true = label_binarize(test_y, classes = label)
    fpr = dict(); tpr = dict(); roc_auc = dict()
    for i in range(len(label)):
        fpr[i], tpr[i], _ = roc_curve(y_true[:, i], y_pred[:, i])
        roc_auc[i] = auc(fpr[i], tpr[i])
    fpr['micro'], tpr['micro'], _ = roc_curve(y_true.ravel(), y_pred.ravel())
    roc_auc['micro'] = auc(fpr['micro'], tpr['micro'])
    all_fpr = np.unique(np.concatenate([fpr[i] for i in range(len(label))]))
    mean_tpr = np.zeros_like(all_fpr)
    for i in range(len(label)):
        mean_tpr += interp(all_fpr, fpr[i], tpr[i])
    mean_tpr /= len(label)
    fpr["macro"] = all_fpr
    tpr["macro"] = mean_tpr
    roc_auc["macro"] = auc(fpr["macro"], tpr["macro"])
    plt.figure()
    plt.plot(fpr["micro"], tpr["micro"],
             label='micro-average ROC curve (area = {0:0.2f})'
                   ''.format(roc_auc["micro"]),
             color='deeppink', linestyle=':', linewidth=4)

    plt.plot(fpr["macro"], tpr["macro"],
             label='macro-average ROC curve (area = {0:0.2f})'
                   ''.format(roc_auc["macro"]),
             color='navy', linestyle=':', linewidth=4)
    for i in range(len(label)):
        y = labelEncoder.inverse_transform(i)
        plt.plot(fpr[i], tpr[i], lw=lw,
                 label='ROC curve of class {0} (area = {1:0.2f})'
                 ''.format(y, roc_auc[i]))

    plt.plot([0, 1], [0, 1], 'k--', lw=lw)
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver operating characteristic to multi-class')
    plt.legend(loc="center left", bbox_to_anchor=(1, 0.5))
    plt.show()
    return fpr, tpr, roc_auc


def Plot_Roc_Curver_Micro_Macro(lg, rf, ksvm, xgbo):
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(16, 6))
    fig.text(0.5, 0.04, 'False Positive Rate', ha='center')
    fig.text(0.04, 0.5, 'True Positive Rate', va='center', rotation='vertical')
    ax1 = fig.add_subplot(1, 2, 1)
    plt.title('micro-average ROC curve')
    plt.rcParams['font.family'] = 'NanumBarunGothicOTF'

    plt.plot([0, 1], [0, 1], 'k--', lw=2)
    plt.plot(
        lg[0]['micro'], lg[1]['micro'], label='logistic (area = {0:0.2f})'.format(lg[2]['micro']))
    plt.plot(
        rf[0]['micro'], rf[1]['micro'], label='Random Forest (area = {0:0.2f})'.format(rf[2]['micro']))
    plt.plot(
        ksvm[0]['micro'], ksvm[1]['micro'], label='Kernel SVM (area = {0:0.2f})'.format(ksvm[2]['micro']))
    plt.plot(
        xgbo[0]['micro'], xgbo[1]['micro'], label='XGBoost (area = {0:0.2f})'.format(xgbo[2]['micro']))
    plt.legend(loc="lower center", bbox_to_anchor=(0.5, -0.35))

    ax2 = fig.add_subplot(1, 2, 2)
    plt.title('macro-average ROC curve')
    plt.rcParams['font.family'] = 'NanumBarunGothicOTF'

    plt.plot([0, 1], [0, 1], 'k--', lw=2)
    plt.plot(
        lg[0]['macro'], lg[1]['macro'], label='logistic (area = {0:0.2f})'.format(lg[2]['macro']))
    plt.plot(
        rf[0]['macro'], rf[1]['macro'], label='Random Forest (area = {0:0.2f})'.format(rf[2]['macro']))
    plt.plot(
        ksvm[0]['macro'], ksvm[1]['macro'], label='Kernel SVM (area = {0:0.2f})'.format(ksvm[2]['macro']))
    plt.plot(
        xgbo[0]['macro'], xgbo[1]['macro'], label='XGBoost (area = {0:0.2f})'.format(xgbo[2]['macro']))
    plt.legend(loc="lower center", bbox_to_anchor=(0.5, -0.35))
    plt.show()

def LoadClassifier(filePath):
    import xgboost as xgb
    import os
    import re
    import pickle
    from keras.models import load_model
    import multiprocessing
    cores = int(multiprocessing.cpu_count())
    fileName = os.path.split(filePath)[1]
    cls_type = re.split('_', fileName)[0]
    if cls_type == 'XGBoost':
        model = xgb.Booster({'nthread' : cores})
        model.load_model(filePath)
    elif cls_type == 'NeuralNetwork':
        cls_type = cls_type+'_'+ re.split('_', fileName)[1]
        model = load_model(filePath)
    else:
        model = pickle.load(open(filePath, 'rb'))
    return cls_type, model

def PredictNewsClassification(infer_vec, clsName, classifier):
    from sklearn.preprocessing import scale
    import numpy as np
    from tqdm import tqdm
    import xgboost as xgb
    tqdm.pandas(desc="progress-bar")
    if clsName.startswith('XGBoost'):
        vecs_w2v = np.concatenate([z.reshape(1, -1) for z in tqdm(map(lambda x: x, infer_vec))])
        vecs_w2v = scale(vecs_w2v)
        dData = xgb.DMatrix(vecs_w2v)
        pred = classifier.predict(dData)
        del dData
    elif clsName.startswith('NeuralNetwork'):
        vecs_w2v = np.concatenate([z.reshape(1, -1) for z in tqdm(map(lambda x: x, infer_vec))])
        vecs_w2v = scale(vecs_w2v)
        pred = classifier.predict_classes(vecs_w2v)
    else:
        pred = classifier.predict(infer_vec)
    return clsName, pred

def MakeTaggedDataDAUM(df, taggedDoc, tagger, stopwords, site):
    from tqdm import tqdm
    tqdm.pandas(desc="progress-bar")
    w2v_docs = list()
    for idx in tqdm(df.index):
        text = df.loc[idx, 'title'] + '.\n' + df.loc[idx,'mainText']
        pos = nav_tokenizer(tagger, text, stopwords)
        category = 'undecided'
        label = [site + '_news_' + str(idx)]
        w2v_docs.append(taggedDoc(pos, label, category))
    return w2v_docs

def nav_tokenizer(tagger, corpus, stopwords):
    pos = tagger.pos(corpus)
    pos = ['/'.join(t) for t in pos if not t[0] in stopwords]
    return pos


def Make_Pre_Data_For_DAUM(model, tfidf, size, data):
    from datetime import datetime
    import numpy as np
    from sklearn.preprocessing import scale
    from tqdm import tqdm
    tqdm.pandas(desc="progress-bar")
    start = datetime.now()
    print(str(model))
    wv = [model[w] for w in tqdm(model.wv.vocab.keys())]
    process1 = datetime.now()
    print('running time : {}'.format(process1 - start))

    print('Vectorizing Data')
    vecs_w2v = np.concatenate(
        [buildWordVector(z, model, size, tfidf) for z in tqdm(map(lambda x: x.words, data))])
    print('scaling Data')
    vecs_w2v = scale(vecs_w2v)
    process2 = datetime.now()
    print('total running time : {}'.format(process2 - start))
    return wv, vecs_w2v

def nav_tokenizer2(tagger, corpus, stopwords):
    pos = tagger.pos(corpus)
    pos = [t[0] for t in pos if not t[0] in stopwords]
    return pos

def MakeTaggedDataDAUM2(df, taggedDoc, tagger, stopwords, site):
    from tqdm import tqdm
    tqdm.pandas(desc="progress-bar")
    w2v_docs = list()
    for idx in tqdm(df.index):
        text = df.loc[idx, 'title'] + '.\n' + df.loc[idx,'mainText']
        pos = nav_tokenizer2(tagger, text, stopwords)
        category = 'undecided'
        label = [site + '_news_' + str(idx)]
        w2v_docs.append(taggedDoc(pos, label, category))
    return w2v_docs

def ExtractModelType(modelName):
    import re, os
    fileName = os.path.split(modelName)[1]
    tagger = re.search('(-ct)|(-mecab)', fileName)
    tagger = tagger.group()[1:]
    if tagger == 'ct' : tagger = 'twitter'
    modelIs = re.search('(Doc2Vec)|(word2vec)|(fastText)', fileName)
    modelIs = modelIs.group()
    if modelIs == 'Doc2Vec':
        modelType = re.search('(dbow)|(dm-c)|(dm-m)', fileName)
        modelType = modelType.group()
    elif modelIs == 'word2vec':
        modelType1 = re.search('(sg-[0-1])', fileName)
        modelType1 = modelType1.group()
        if re.search('[0-1]', modelType1).group() == '1':
            modelType1 = 'skip-gram'
        else:
            modelType1 = 'CBOW'
        modelType2 = re.search('cbow_mean-[0-1]', fileName)
        modelType2 = modelType2.group()
        modelType = modelType1 + '_' + modelType2
    elif modelIs == 'fastText':
        modelType1 = re.search('(sg-[0-1])', fileName)
        modelType1 = modelType1.group()
        if re.search('[0-1]', modelType1).group() == '1':
            modelType1 = 'skip-gram'
        else:
            modelType1 = 'CBOW'
        modelType2 = re.search('cbow_mean-[0-1]', fileName)
        modelType2 = modelType2.group()
        modelType = modelType1 + '_' + modelType2
    modelIs = '{}_{}'.format(modelIs,modelType)
    return modelIs, tagger

def PredictSentiment(infer_vec, clsName, classifier):
    from sklearn.preprocessing import scale
    import numpy as np
    from tqdm import tqdm
    import xgboost as xgb
    from itertools import chain
    #tqdm.pandas(desc="progress-bar")
    if clsName.startswith('XGBoost'):
        #vecs_w2v = np.concatenate([z.reshape(1, -1) for z in tqdm(map(lambda x: x, infer_vec))])
        vecs_w2v = np.concatenate([z.reshape(1, -1) for z in map(lambda x: x, infer_vec)])
        vecs_w2v = scale(vecs_w2v)
        dData = xgb.DMatrix(vecs_w2v)
        pred = classifier.predict(dData)
        pred = pred.round()
        del dData
    elif clsName.startswith('NeuralNetwork'):
        #vecs_w2v = np.concatenate([z.reshape(1, -1) for z in tqdm(map(lambda x: x, infer_vec))])
        vecs_w2v = np.concatenate([z.reshape(1, -1) for z in map(lambda x: x, infer_vec)])
        vecs_w2v = scale(vecs_w2v)
        pred = classifier.predict_classes(vecs_w2v)
        pred = np.array(list(chain.from_iterable(pred)))
    else:
        pred = classifier.predict(infer_vec)
    return clsName, pred

def Read_Comments(row):
    import pandas as pd
    import Database_Handler as dh
    mongodb = dh.ToMongoDB(*dh.GCP_MongoDB_Information())
    dbname = 'hy_db'
    useDB = dh.Use_Database(mongodb, dbname)
    commentCollection = dh.Use_Collection(useDB, 'comments')
    info = {'site': row['site'],
            'category': row['category'],
            'date': row['date'],
            'rank': str(row['rank'])}
    commentsForNews = commentCollection.find(info)
    commentsForNews = pd.DataFrame(list(commentsForNews))
    realNumCount = commentsForNews.shape
    print(realNumCount)
    return commentsForNews

def Make_Comments_File(filepath, row):
    import Basic_Module as bm
    import os
    filename = row.name
    absPath = os.path.join(filepath, filename + '.csv')
    if os.path.isfile(absPath):
        pass
    else:
        comments = bm.Read_Comments(row)
        comments.to_csv(absPath, index=None, header=True, encoding='utf-8')

def Read_Comments2(row):
    import pandas as pd
    import Database_Handler as dh
    mongodb = dh.ToMongoDB(*dh.GCP_MongoDB_Information())
    dbname = 'hy_db'
    useDB = dh.Use_Database(mongodb, dbname)
    commentCollection = dh.Use_Collection(useDB, 'comments')
    info = {'site': row['site'],
            'category': row['category'],
            'date': row['date'],
            'rank': int(row['rank'])}
    commentsForNews = commentCollection.find(info)
    commentsForNews = pd.DataFrame(list(commentsForNews))
    realNumCount = commentsForNews.shape
    print(realNumCount)
    return commentsForNews

def Make_Comments_File2(filepath, row):
    import Basic_Module as bm
    import os
    filename = row.name
    absPath = os.path.join(filepath, filename + '.csv')
    if os.path.isfile(absPath):
        pass
    else:
        comments = Read_Comments2(row)
        comments.to_csv(absPath, index=None, header=True, encoding='utf-8')

# row : index : id
# file : <>.csv
def Read_CommentsFile(filepath, row):
    import os
    import pandas as pd
    filename = row.name + '.csv'
    absFilePath = os.path.join(filepath, filename)
    df = pd.read_csv(absFilePath, encoding='utf-8', header=0, index_col=None)
    df = df[~df.comments.isna()]
    df = df[df.comments.str.match('.+[0-9a-zA-Z가-힣ㄱ-하-ㅣ]+')]
    # 댓글중에서 문자가 적어도 하나는 있는 것만.
    return df


def TokenizeAndTag(tagger, row, stopwords, tagDoc):
    pos = nav_tokenizer(tagger, row.comments, stopwords)
    category = 'comments'
    label = [row.site + '_' + row.category.strip() + '_' + row.date + '_' + str(row['rank']) + '_' + str(row.name)]
    return tagDoc(pos, label, category)

def Get_infter_Vectors_For_Comments(path, row, tagger, stopwords, taggedFormat, model):
    df = Read_CommentsFile(path, row)
    tagged = df.apply(lambda x: TokenizeAndTag(tagger, x, stopwords, taggedFormat), axis=1).tolist()
    infer_vectors = Get_Infer_Vector(tagged, model)
    return df, infer_vectors, row.name

def RunClassifier(rawdata, infer_vectors, path, name):
    import warnings
    warnings.filterwarnings('ignore')
    from glob import glob
    import pandas as pd
    classifierList = glob(path + '*' + name)
    loadClassifierDict = dict(map(lambda x: LoadClassifier(x), classifierList))
    df = dict(map(lambda x: PredictSentiment(infer_vectors, x, loadClassifierDict[x]), loadClassifierDict))
    df = pd.DataFrame.from_dict(df)
    df = rawdata.merge(df, left_index=True, right_index=True)
    return df

def PipeLineForSentimentAnalysis(dataPath,classifierPath, outcomePath, row, tagger, stopwords, tagDoc, model, name):
    import os
    df, infer_vectors, targetNewsId = Get_infter_Vectors_For_Comments(dataPath, row, tagger, stopwords, tagDoc, model)
    outcomeClassifier = RunClassifier(df, infer_vectors, classifierPath, name)
    reName = 'outcome_comments_sentiment_for_{}_news_{}'.format(row.site, name)
    if os.path.isdir(os.path.join(outcomePath, targetNewsId)):
        outcomeName = os.path.join(outcomePath, targetNewsId, reName+'.csv')
    else:
        os.mkdir(os.path.join(outcomePath, targetNewsId))
        outcomeName = os.path.join(outcomePath, targetNewsId, reName+'.csv')
    outcomeClassifier.to_csv(outcomeName, index=None, encoding = 'utf-8')