import sys
import time

start_time = time.time()

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

def precision(gold_data, pred_data):
    good = 0.0
    bad = 0.0
    for id_sentence, relation in gold_data.iteritems():
        if id_sentence in pred_data:
            if relation["person"] == pred_data[id_sentence]["person"] and relation["location"] == pred_data[id_sentence]["location"]:
                good += 1
            else:
                bad += 1
        else:
            bad += 1
    return good/(good+bad)

if __name__ == '__main__':
    gold_file = sys.argv[1]
    predicted_file = sys.argv[2]
    gold_data = read_annotation_files(gold_file)
    pred_data = read_annotation_files(predicted_file)
    prec = precision(gold_data, pred_data)
    print "Precision is " + str(prec)
