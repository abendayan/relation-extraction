import sys
import time
import utils as ut
import numpy as np
from collections import OrderedDict
from sklearn import metrics, svm
import pickle
import itertools
import scipy
start_time = time.time()
TARGET_TAG = { 1 : "Live_In", 0 : "Other_Tag" }
TAG_TO_PREDICT = "Live_In"
LOCATION_NER = { 'GPE', 'FACILITY', 'LOC' }
LOCATION_ALTER_NER = { 'ORG' }
PERSON_NER = { 'PERSON' }

def passed_time(previous_time):
    return round(time.time() - previous_time, 3)

def create_annotations_file(output_file, predicted, tagg_info):
    file_output = open(output_file, "w")
    to_write = ""
    index = 0
    for i, predict in enumerate(predicted):
        sentence, chunk = tagg_info[i]
        left, right = chunk
        # if sentence == 1483:
            # print TARGET_TAG[predict]
            # print chunk
        if TARGET_TAG[predict] == TAG_TO_PREDICT:
        # if TARGET_TAG[predict] == TAG_TO_PREDICT or ut.entity_to_loc(left[-1]["ner"]) == "PERSON" and ut.entity_to_loc(right[-1]["ner"]) == "LOCATION":

            # print sentence
            to_write += "sent" + str(sentence) + "\t"

            to_write += ut.chunk_phrase(left)
            to_write += "\t" + TAG_TO_PREDICT + "\t"
            to_write += ut.chunk_phrase(right) + "\n"
            # print sentence
            # print chunk
            # gvhj
    # for id_sent, dic in sentences.iteritems():
    #     sentence = dic["words"]
    #     to_write += "sent" + str(id_sent) +"\t"
    #     to_write += features_ix[features[index][0]] + "\t"
    #     to_write += TARGET_TAG[predicted[index]] + "\t"
    #     to_write += features_ix[features[index][1]] + "\n"
    #     index += 1
    file_output.write(to_write)
    print "Finish writing in the output annotation file in " + str(passed_time(start_time))

def build_datas(sentences, features_all):
    features_array = []
    tagging_info = []
    for id_sentence, dic in sentences.iteritems():
        sentence = dic['words']
        chunk = itertools.permutations(ut.extract_chunks(sentence), 2)
        for chunk_pair in chunk:
            m1Phrase = ut.chunk_phrase(chunk_pair[0])
            m2Phrase = ut.chunk_phrase(chunk_pair[1])
            connect = ut.AnnotConnection(m1Phrase, m2Phrase)
            feat_sent = ut.Features(chunk_pair[0], chunk_pair[1], sentence)
            features = []
            for feat in feat_sent.feat:
                # if feat not in features_all:
                #     features_all[feat] = len(features_all)
                #     features_ix[features_all[feat]] = feat

                if feat in features_all:
                    features.append(features_all[feat])
            # if id_sentence == 1483:
            #     print m1Phrase, m2Phrase
            features_array.append(features)
            tagging_info.append((id_sentence, chunk_pair))
    inflated_feats = []
    for dense in features_array:
        sparse = np.zeros(len(features_all))
        for i in dense:
            sparse[i] = 1
        inflated_feats.append(sparse)
    return scipy.sparse.csr_matrix(inflated_feats), tagging_info

if __name__ == '__main__':
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    type_input = input_file.split(".")[-1]
    if type_input != "processed":
        print "The input file " + input_file + " is not in the format .processed"
        sys.exit(0)
    sentences = ut.build_corpus(open(input_file, "r").read().split("\n"))
    print "Corpus read"
    clf, features_learn = pickle.load(open('model.pkl', 'rb'))
    features_ix = { feat:id for id, feat in features_learn.iteritems() }
    # predicted = clf.predict(features)
    # print features_learn
    features, tagging_info = build_datas(sentences, features_learn)
    # print features
    predicted = clf.predict(features)
    create_annotations_file(output_file, predicted, tagging_info)
