import sys
import time
from collections import OrderedDict
from sklearn import metrics, svm
import itertools
import pickle
import numpy as np

start_time = time.time()
TARGET_TAG = "Live_In"
LOCATION_NER = { 'GPE', 'FACILITY', 'LOC' }
LOCATION_ALTER_NER = { 'ORG' }
PERSON_NER = { 'PERSON' }
LABELS = { 'Live_In' : 1, 'Other_Tag' : 0 }

def passed_time(previous_time):
    return round(time.time() - previous_time, 3)

def read_annotation_files(name_file):
    annotations = {}
    sentences = open(name_file, "r").read().split("\n")
    for sentence in sentences:
        if sentence != "":
            sentence = sentence.split("(")[0]
            id_text = int(sentence.split("\t")[0].replace("sent", ""))
            sentence = sentence.replace("sent"+ str(id_text) + "\t", "")
            m1, tag, m2, _ = sentence.split("\t")
            annotations[id_text] = {}
            annotations[id_text][AnnotConnection(m1, m2)] = LABELS[label_or_not(tag)]
    return annotations

def label_or_not(tag):
    if tag == TARGET_TAG:
        return tag
    return 'Other_Tag'

def build_corpus(words):
    sentence = []
    sentences = {}
    for word in words:
        if word != "":
            sentence.append(word)
        else:
            if sentence != []:
                build_sentence(sentence, sentences)
            sentence = []
    return sentences

def build_sentence(sentence, sentences):
    id_text = sentence[0].replace("#id: sent", "")
    text = sentence[1].replace("#text: ", "")
    id_number = int(id_text)
    sentences[id_number] = OrderedDict()
    sentences[id_number]["text"] = text
    sentences[id_number]["words"] = {}

    sentence = sentence[2:]
    for word_ent in sentence:
        words = {}
        words_ent = word_ent.split("\t")
        words["word"] = words_ent[1]
        words["lemma"] = words_ent[2]
        words["pos"] = words_ent[3]
        words["tag"] = words_ent[4]
        words["parent"] = int(words_ent[5])
        words["dep"] = words_ent[6]
        words["bio"] = words_ent[7]
        if words["bio"] != 'O':
            words["ner"] = words_ent[8]
        else:
            words["ner"] = ""
        sentences[id_number]["words"][int(words_ent[0])] = words

class AnnotConnection:
    def __init__(self, m1, m2):
        self.m1 = m1
        self.m2 = m2

    def __eq__(self, connect):
        if isinstance(connect, AnnotConnection):
            return self.m1 == connect.m1 and self.m2 == connect.m2
        return false

    def __repr__(self):
        return '(m1=%s, m2=%s)' % (self.m1, self.m2)

    def __hash__(self):
        return hash(self.__repr__())

def build_datas(annotations, sentences):
    features_all = {}
    features_array = []
    labels = []
    for id_sentence, dic in sentences.iteritems():
        sentence = dic['words']
        chunk = itertools.permutations(extract_chunks(sentence), 2)
        for chunk_pair in chunk:
            annot = annotations[id_sentence]
            m1Phrase = chunk_phrase(chunk_pair[0])
            m2Phrase = chunk_phrase(chunk_pair[1])
            connect = AnnotConnection(m1Phrase, m2Phrase)
            correct, label = False, 0
            for key in annot:
                if (key.m1 in m1Phrase or m1Phrase in key.m1) and (key.m2 in m2Phrase or m2Phrase in key.m2):
                    correct, label = True, annot[key]
            labels.append(label)
            feat_sent = Features(chunk_pair[0], chunk_pair[1], sentence)
            features = []
            for feat in feat_sent.feat:
                if feat not in features_all:
                    features_all[feat] = len(features_all)
                features.append(features_all[feat])
            features_array.append(features)
    return np.array(features_array), np.array(labels), features_all

class Features:
    def __init__(self, m1, m2, sentence):
        self.m1 = m1
        self.m2 = m2
        self.feat = []
        self.build_features(sentence)
    def build_features(self, sentence):
        # m1 : last word
        # m2 : last word
        # TODO finish
        self.feat.append(self.m1[-1]['word'])
        self.feat.append(self.m2[-1]['word'])
def chunk_phrase(chunks):
    phrase = ""
    for chunk in chunks:
        phrase += chunk['word'] + ' '
    return phrase[:-1]

def extract_chunks(words):
    i = 0
    chunks = []
    chunk = []
    for id, word in words.iteritems():
        if word['bio'] in {'O','B'}:
            if chunk:
                chunks.append(chunk)
            chunk = []
        if word['bio'] in {'I','B'}:
            chunk.append(word)
        i +=1
    return chunks

def persist_model(clf, features):
    pickle.dump((clf, features), open('model.pkl', 'wb'))

if __name__ == '__main__':
    corpus_file = sys.argv[1]
    annot_file = sys.argv[2]
    annotations = read_annotation_files(annot_file)
    print "Read annotation files " + str(passed_time(start_time))
    sentences = build_corpus(open(corpus_file, "r").read().split("\n"))
    print "Read the corpus " + str(passed_time(start_time))
    features, tags, all_features = build_datas(annotations, sentences)
    print "Build the features " + str(passed_time(start_time))
    clf = svm.LinearSVC()
    clf.fit(features, tags)
    persist_model(clf, all_features)
    # features = Features(corpus_file, annot_file)
    #
    # clf = svm.LinearSVC()
    # clf.fit(features.annotations, features.labels)
