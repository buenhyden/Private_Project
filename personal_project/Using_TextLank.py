from konlpy.tag import Twitter
from ckonlpy.tag import Twitter as CTwitter
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer, TfidfTransformer
from sklearn.preprocessing import normalize as sknorm
import pandas as pd
import re
import numpy as np

ot = Twitter()
ct = CTwitter()

def PressList():
    pressList = pd.read_excel('./data/presslist.xlsx')
    return pressList['언론사'].tolist()
class SentenceTokenizer(object):
    def __init__(self):
        self.twitter = ot
        self.ctwitter = ct
        # self.mecab = mecab

        # self.stopwords = stopwords
        self.stopwords = ['중인', '만큼', '마찬가지', '꼬집었', "기자", "아", "휴", "아이구",
                          "아이쿠", "아이고", "어", "나", "우리", "저희", "따라", "의해", "을", "를", "에", "가"] + PressList()

    def text2sentences(self, text):
        sentences = re.sub('\. ', '.\n', text).split('\n')
        for idx in range(0, len(sentences)):
            if len(sentences[idx]) <= 10:
                sentences[idx - 1] += (' ' + sentences[idx])
                sentences[idx] = ''
        return sentences

    def get_nouns(self, sentences):
        nouns = []
        for sentence in sentences:
            if sentence is not '':
                nouns.append(' '.join([noun for noun in self.ctwitter.phrases(str(sentence))
                                       if noun not in self.stopwords and len(noun) > 1]))
                nouns.append(' '.join([noun for noun in self.ctwitter.nouns(str(sentence))
                                       if noun not in self.stopwords and len(noun) > 1]))
                nouns.append(' '.join([noun for noun in self.ctwitter.morphs(str(sentence))
                                       if noun not in self.stopwords and len(noun) > 1]))
        nouns = list(set(nouns))
        return nouns


class GraphMatrix(object):
    def __init__(self):
        self.tfidf = TfidfVectorizer(ngram_range=(1, 5), sublinear_tf=True, lowercase=False)
        self.cnt_vec = CountVectorizer(ngram_range=(1, 5), lowercase=False)
        self.graph_sentence = []

    def build_sent_graph(self, sentence):
        tfidf_mat = self.tfidf.fit_transform(sentence).toarray()
        # tfidf_mat = self.tfidf.fit_transform(sentence).toarray()
        self.graph_sentence = np.dot(tfidf_mat, tfidf_mat.T)
        return self.graph_sentence

    def build_words_graph(self, sentence):
        cnt_vec_mat = sknorm(self.cnt_vec.fit_transform(sentence).toarray().astype(float), axis=0)
        vocab = self.cnt_vec.vocabulary_
        return np.dot(cnt_vec_mat.T, cnt_vec_mat), {vocab[word]: word for word in vocab}


class Rank(object):
    def get_ranks(self, graph, d=0.85):  # d = damping factor
        A = graph
        matrix_size = A.shape[0]
        for id in range(matrix_size):
            A[id, id] = 0  # diagonal 부분을 0으로
            link_sum = np.sum(A[:, id])  # A[:, id] = A[:][id]
            if link_sum != 0:
                A[:, id] /= link_sum
            A[:, id] *= -d
            A[id, id] = 1
        B = (1 - d) * np.ones((matrix_size, 1))
        ranks = np.linalg.solve(A, B)  # 연립방정식 Ax = b
        return {idx: r[0] for idx, r in enumerate(ranks)}


class TextRankX(object):
    def __init__(self, text):
        self.sent_tokenize = SentenceTokenizer()
        self.sentences = self.sent_tokenize.text2sentences(text)
        self.nouns = self.sent_tokenize.get_nouns(self.sentences)
        self.graph_matrix = GraphMatrix()
        self.sent_graph = self.graph_matrix.build_sent_graph(self.nouns)
        self.words_graph, self.idx2word = self.graph_matrix.build_words_graph(self.nouns)
        self.rank = Rank()
        self.sent_rank_idx = self.rank.get_ranks(self.sent_graph)
        self.sorted_sent_rank_idx = sorted(self.sent_rank_idx, key=lambda k: self.sent_rank_idx[k], reverse=True)
        self.word_rank_idx = self.rank.get_ranks(self.words_graph)
        self.sorted_word_rank_idx = sorted(self.word_rank_idx, key=lambda k: self.word_rank_idx[k], reverse=True)

    def summarize(self, sent_num=3):
        summary = []
        index = []
        for idx in self.sorted_sent_rank_idx[:sent_num]:
            index.append(idx)
        index.sort()
        for idx in index:
            summary.append(self.sentences[idx])
        return summary

    def keywords(self, word_num=10):
        rank = Rank()
        rank_idx = rank.get_ranks(self.words_graph)
        sorted_rank_idx = sorted(rank_idx, key=lambda k: rank_idx[k], reverse=True)
        keywords = []
        index = []
        for idx in sorted_rank_idx[:word_num]:
            index.append(idx)
        # index.sort()
        for idx in index:
            keywords.append(self.idx2word[idx])
        return keywords

if __name__ == '__main__':
    text = """경구용 피임약은 여성호르몬을 강제로 조정해 배란을 억제하는 원리다. 호르몬 변화로 인해 신체에 다양한 증상이 함께 나타난다. 유방암과 우울증 위험을 높인다는 연구결과가 있는 반면, 류마티스 관절염 위험을 낮춘다는 연구결과도 있다.
        최근에는 피임약 복용이 이성의 취향까지 바꾼다는 연구결과가 발표됐다. 이성을 선택할 때 선호하는 얼굴을 바꾼다는 내용의 연구다. 영국 스코틀랜드 스털링대학 연구진은 피임약을 복용하는 만18~24세 여성 18명과 복용하지 않는 37명을 대상으로 각각 2회에 걸쳐 취향을 조사했다.
        조사에 사용된 얼굴은 컴퓨터 그래픽으로 남녀 20명의 사진을 합성해서 만들었다. 모니터에 매력적이라고 생각하는 얼굴이 나타나면 선택하도록 했다. 첫 번째 조사는 두 그룹 모두 피임약을 복용하지 않을 때 진행했다. 그 중에서도 임신 가능성이 가장 높은 배란 1~2일 전에 조사가 이뤄졌다. 두 번째 조사 역시 배란기에 해당하는 시기에 이뤄졌다. 다만, 한 그룹은 피임약을 복용하는 상태였다.
        그 결과, 피임약을 복용하지 않은 그룹은 두 차례의 조사에서 모두 남성적인 얼굴에서 매력을 느끼는 것으로 조사됐다. 반면, 피임약을 복용한 그룹의 경우 복용 전에는 남성적인 얼굴에 매력을 느끼다가 복용 후에는 이 비율이 매우 낮아졌다.
            """
    x = TextRankX(text)
    print (x.keywords())