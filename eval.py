import sys
import time
import random

start_time = time.time()
ERROR_ANALYS = True
TARGET_TAG = 'Live_In'

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
            if TARGET_TAG in sentence:
                person, location = sentence.split(TARGET_TAG)
                person = person.replace("\t", "")
                location = location.replace("\t", "")
                annotations[id_text] = {}
                annotations[id_text]["person"] = person
                annotations[id_text]["location"] = location
    return annotations

def error_analysis(mistakes):
    print "="*20
    print "ANALISIS OF ERRORS"
    print "="*20
    to_analyse = random.sample(mistakes, 5)
    for errors in to_analyse:
        print "Sentence " + str(errors[0])
        print "Gold : "
        print errors[1]
        print "Pred : "
        print errors[2]


def precision(gold_data, pred_data):
    good = 0.0
    bad = 0.0
    mistakes = []
    for id_sentence, relation in gold_data.iteritems():
        if id_sentence in pred_data:
            if relation["person"] == pred_data[id_sentence]["person"] and relation["location"] == pred_data[id_sentence]["location"]:
                good += 1
            else:
                bad += 1
                mistakes.append([id_sentence, relation, pred_data[id_sentence]])
        else:
            bad += 1
    if ERROR_ANALYS:
        error_analysis(mistakes)
    return good/(good+bad)

# TODO the recall

if __name__ == '__main__':
    gold_file = sys.argv[1]
    predicted_file = sys.argv[2]
    gold_data = read_annotation_files(gold_file)
    pred_data = read_annotation_files(predicted_file)
    prec = precision(gold_data, pred_data)
    print "Precision is " + str(prec)
