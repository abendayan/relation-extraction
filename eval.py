import sys
import time
import random

start_time = time.time()
ERROR_ANALYS = True
TARGET_TAG = 'Live_In'

def passed_time(previous_time):
    return round(time.time() - previous_time, 3)

def read_annotation_files(name_file):
    annotations = []
    sentences = open(name_file, "r").read().split("\n")
    for sentence in sentences:
        if sentence != "":
            sentence = sentence.split("(")[0]
            id_text = sentence.split("\t")[0].replace("sent", "")
            sentence = sentence.replace("sent"+ str(id_text) + "\t", "")
            if TARGET_TAG in sentence:
                person, location = sentence.split(TARGET_TAG)
                person = person.replace("\t", "")
                location = location.replace("\t", "")
                annotations.append(id_text + " " +  person + " " + TARGET_TAG + " " + location )
                # annotations[id_text]["person"] = person
                # annotations[id_text]["location"] = location
    return annotations

def error_analysis(mistakes):
    # to_analyse = mistakes[:5]
    to_analyse = random.sample(mistakes, 5)
    for errors in to_analyse:
        print "Relation :"
        print errors


def precision(gold_data, pred_data):
    good = 0.0
    bad = 0.0
    mistakes = []
    for pred in pred_data:
        if pred in gold_data:
            good += 1
        else:
            bad += 1
            mistakes.append(pred)
    if ERROR_ANALYS:
        print "="*20
        print "ANALISIS OF ERRORS PRECISION (relations not in gold)"
        print "="*20
        error_analysis(mistakes)
    return good/(good+bad)

def recall(gold_data, pred_data):
    good = 0.0
    bad = 0.0
    mistakes = []
    for gold in gold_data:
        if gold in pred_data:
            good += 1
        else:
            bad += 1
            mistakes.append(gold)
    if ERROR_ANALYS:
        print "="*20
        print "ANALISIS OF ERRORS RECALL (relations not in pred)"
        print "="*20
        error_analysis(mistakes)
    return good/(good+bad)


if __name__ == '__main__':
    gold_file = sys.argv[1]
    predicted_file = sys.argv[2]
    gold_data = read_annotation_files(gold_file)
    pred_data = read_annotation_files(predicted_file)
    prec = precision(gold_data, pred_data)
    print "Precision is " + str(prec)
    rec = recall(gold_data, pred_data)
    print "Recall is " + str(rec)
