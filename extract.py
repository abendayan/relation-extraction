import sys
import time
import utils as ut
import numpy as np
from collections import OrderedDict
from sklearn import metrics, svm
import pickle
import itertools
import scipy
import pdb
from sklearn.externals import joblib
start_time = time.time()
TARGET_TAG = {1: "Live_In", 0 : "Other_Tag" }
TAG_TO_PREDICT = "Live_In"
LOCATION_NER = { 'GPE', 'FACILITY', 'LOC' }
LOCATION_ALTER_NER = { 'ORG' }
PERSON_NER = { 'PERSON' }

def passed_time(previous_time):
    return round(time.time() - previous_time, 3)

def check_entity_chunk_phrase(phrase):
    for chunk in phrase:
        if ut.entity_to_pers(chunk["ner"]) != "PERSON":
            return False
    return True

def connected(sentence, left, right):
    pattern = ["from", "of"]
    not_in = ["manager"]
    pattern_of = ["home"]
    pattern_in = ["live", "living", "stay", "staying", "lived", "representative"]
    if check_entity_chunk_phrase(left) and (ut.in_gazette(ut.chunk_phrase(right) or ut.entity_to_loc(right[-1]))):
        start = False
        found = False
        for id, word in sentence.iteritems():
            if word["id"] == left[-1]["id"]:
                start = True
            if word["id"] == right[0]["id"]:
                break
            if start:
                if word["lemma"] in pattern_in and id+1 in sentence:
                    if sentence[id+1]["lemma"] == "in":
                        found = True
                if word["lemma"] in pattern_of and id+1 in sentence:
                    if sentence[id+1]["lemma"] == "of":
                        found = True
                if word["lemma"] in pattern:
                    if id-1 in sentence:
                        if not sentence[id-1]["lemma"] in not_in:
                            found = True
                # if ut.in_gazette(word["lemma"]):
                #     found = False
        return found
    #     parent = right[0]["parent"]
    #     id_right = right[0]["id"]
    #     found = False
    #     while parent != left[-1]["id"] and parent != 0:
    #         parent = sentence[parent]["parent"]
    #         if parent != 0 and sentence[parent]["lemma"] in pattern:
    #             found = True
    #         id_right = parent
    #     parent = left[0]["parent"]
    #     id_left = left[0]["id"]
    #     while parent != right[-1]["id"] and parent != 0:
    #         parent = sentence[parent]["parent"]
    #         if parent != 0 and sentence[parent]["lemma"] in pattern:
    #             found = True
    #         id_left = parent
    #     if id_right == id_left:
    #         return found
    return False

def create_annotations_file(output_file, predicted, tagg_info, sentences):
    file_output = open(output_file, "w")
    to_write = ""
    index = 0
    for i, predict in enumerate(predicted):
        id_sentence, chunk = tagg_info[i]
        left, right = chunk
        if predict == 1 or (predict == 0 and connected(sentences[id_sentence]["words"], left, right)):
             # and (ut.entity_to_loc(right[-1])=="LOCATION" or ut.in_gazette(ut.chunk_phrase(right))):
                # print sentence
                # print ut.chunk_phrase(left)
                # # if sentence == 1147:
                # #     pdb.set_trace()
                # #     ut.entity_to_loc(right[-1])
                # print ut.chunk_phrase(right)
                # print ut.entity_to_loc(right[-1])
            to_write += "sent" + str(id_sentence) + "\t"
            to_write += ut.chunk_phrase(left)
            to_write += "\t" + TAG_TO_PREDICT + "\t"
            to_write += ut.chunk_phrase(right) + "\n"

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
                if feat in features_all:
                    features.append(features_all[feat])
                else:
                    features.append(features_all["UNK"])

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
    if type_input != "txt":
        print "The input file " + input_file + " is not in the format .processed"
        sys.exit(0)
    sentences = ut.build_corpus(open(input_file, "r").read().split("\n"))
    print "Corpus read"
    clf = joblib.load('model.pkl')
    features_learn = pickle.load(open('feature.pkl', 'rb'))
    features_ix = { feat:id for id, feat in features_learn.iteritems() }
    features, tagging_info = build_datas(sentences, features_learn)
    predicted = clf.predict(features)
    create_annotations_file(output_file, predicted, tagging_info, sentences)
