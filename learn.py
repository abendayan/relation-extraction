import sys
import time
import utils as ut
from collections import OrderedDict
from sklearn import metrics, svm
import itertools
import pickle
import numpy as np
import scipy
import pdb
from sklearn.externals import joblib

start_time = time.time()
TARGET_TAG = "Live_In"
LOCATION_NER = { 'GPE', 'FACILITY', 'LOC' }
LOCATION_ALTER_NER = { 'ORG' }
PERSON_NER = { 'PERSON' }
TAGS = {'OrgBased_In', 'Located_In', 'Work_For', 'Kill', 'Live_In'}
LABELS =   {'OrgBased_In':5, 'Located_In': 4, 'Work_For' : 3, 'Kill' : 2, "Live_In" : 1, "Other_Tag" : 0 }
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
            if id_text not in annotations:
                annotations[id_text] = []
            annotations[id_text].append((ut.AnnotConnection(m1, m2), LABELS[label_or_not(tag)]))
    return annotations

def label_or_not(tag):
    if tag in TAGS:
        return tag
    return 'Other_Tag'

def build_datas(annotations, sentences):
    features_all = {}
    features_array = []
    labels = []
    for id_sentence, dic in sentences.iteritems():
        sentence = dic['words']
        chunk = itertools.permutations(ut.extract_chunks(sentence), 2)

        features_chunks = []
        size = 0
        for chunk_pair in chunk:
            size += 1
            for annot, tag in annotations[id_sentence]:
                m1Phrase = ut.chunk_phrase(chunk_pair[0])
                m2Phrase = ut.chunk_phrase(chunk_pair[1])
                connect = ut.AnnotConnection(m1Phrase, m2Phrase)
                correct, label = False, 0
                if (annot.m1 == m1Phrase or annot.m1 == m1Phrase + "." or annot.m1 == m1Phrase + " .") \
                and (annot.m2 == m2Phrase or annot.m2 == m2Phrase + "." or annot.m2 == m2Phrase + " ."):
                    correct, label = True, tag

                labels.append(label)
                feat_sent = ut.Features(chunk_pair[0], chunk_pair[1], sentence)
                features = []
                for feat in feat_sent.feat:
                    if feat not in features_all:
                        features_all[feat] = len(features_all)
                    features.append(features_all[feat])
                features_array.append(features)

    inflated_feats = []
    for dense in features_array:
        sparse = np.zeros(len(features_all))
        for i in dense:
            sparse[i] = 1
        inflated_feats.append(sparse)
    A = np.array(inflated_feats)
    return scipy.sparse.csr_matrix(A), np.array(labels), features_all


def save_model(clf, features):
    joblib.dump(clf, 'model.pkl')
    pickle.dump(features, open('feature.pkl', 'wb'))

if __name__ == '__main__':
    corpus_file = sys.argv[1]
    annot_file = sys.argv[2]
    annotations = read_annotation_files(annot_file)
    print "Read annotation files " + str(passed_time(start_time))
    sentences = ut.build_corpus(open(corpus_file, "r").read().split("\n"))
    print "Read the corpus " + str(passed_time(start_time))
    features, tags, all_features = build_datas(annotations, sentences)
    print "Build the features " + str(passed_time(start_time))
    clf = svm.LinearSVC()
    clf.fit(features, tags)
    save_model(clf, all_features)
    print "Saved model " + str(passed_time(start_time))
