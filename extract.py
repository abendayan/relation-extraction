import sys
import time
from collections import OrderedDict

start_time = time.time()
TARGET_TAG = { "Live_In" : 1, "No_Tag" : 0 }
LOCATION_NER = { 'GPE', 'FACILITY', 'LOC' }
LOCATION_ALTER_NER = { 'ORG' }
PERSON_NER = { 'PERSON' }

def passed_time(previous_time):
    return round(time.time() - previous_time, 3)


class Annotation:
    def __init__(self, name_file):
        print "Reading the file " + name_file
        words = open(name_file, "r").read().split("\n")
        self.sentences = OrderedDict()
        self.annotations = OrderedDict()
        self.build_corpus(words)
        print "File " + name_file + " read, finish in " + str(passed_time(start_time))
        self.create_annotations()
        print "Finish building the annotations " + str(passed_time(start_time))

    def build_corpus(self, words):
        sentence = []
        for word in words:
            if word != "":
                sentence.append(word)
            else:
                if sentence != []:
                    self.build_sentence(sentence)
                sentence = []

    def build_sentence(self, sentence):
        id_text = sentence[0].replace("#id: sent", "")
        text = sentence[1].replace("#text: ", "")
        id_number = int(id_text)
        self.sentences[id_number] = OrderedDict()
        self.sentences[id_number]["text"] = text
        self.sentences[id_number]["words"] = OrderedDict()

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
            self.sentences[id_number]["words"][int(words_ent[0])] = words

    def filter_person(self, words, id_word):
        person = []
        j = id_word-1
        while j > 0 and ("ner" not in words[j] or words[j]["ner"] not in PERSON_NER):
            j-=1
        k = j
        while k > 0 and "ner" in words[k] and words[k]["ner"] in PERSON_NER:
            k-=1
        if k == 0 or "ner" not in words[k] or words[k]["ner"] not in PERSON_NER:
            k += 1
        while k <= j:
            person.append(words[k]["word"])
            k += 1
        return person

    def search_person_connected(self, words, person, parent):
        for id_word, word in words.iteritems():
            if word["parent"] == parent and "ner" in word and word["ner"] in PERSON_NER:
                person.insert(0, word["word"])

    def create_annotations(self):
        for id_sent, dic in self.sentences.iteritems():
            location = []
            person = []
            text = dic["text"]
            words = dic["words"]
            found_location = False
            found_person = False
            found = False
            for id_word, word in words.iteritems():
                if word["word"] in ["home", "live"]:
                    for id, word_test in words.iteritems():
                        if id > id_word:
                            break
                        if word_test["ner"] in PERSON_NER:
                            person = [word_test["word"]]
                            self.search_person_connected(words, person, id)
                            found_person = True
                    location = []
                    for id in range(id_word, len(words)):
                        if words[id]["ner"] in LOCATION_NER:
                            location.append(words[id]["word"])
                            found_location = True
                    break
                elif word["ner"] in LOCATION_NER and not found_person:
                    location.append(word["word"])
                    found_location = True
                elif word["ner"] in PERSON_NER and found_location:
                    if id_word + 1 in words and words[id_word+1]["word"] == "'s":
                        location = []
                        found_location = False
                    person = [word["word"]]
                    self.search_person_connected(words, person, id_word)
                    found_person = True



                # elif "ner" in word:
                #     if word["ner"] in LOCATION_NER:
                #         if found_person:
                #             location.append(word["word"])
                #         else:
                #             found_location = True
                #             parent = word["parent"]
                #             found = False
                #             while parent != 0:
                #                 if "ner" in words[parent]:
                #                     if words[parent]["ner"] in PERSON_NER:
                #                         found = True
                #                         break
                #                 parent = words[parent]["parent"]
                #             if found:
                #                 location.append(word["word"])
                #                 found_person = True
                #                 person = [words[parent]["word"]]
                #                 self.search_person_connected(words, person, parent)
                        # if id_word == 1 or words[id_word-1]["lemma"] != "to":
                        #     found_location = True
                        #     location.append(word["word"])
                        #     parent = word["parent"]
                        #     found = False
                        #     while parent != 0:
                        #         if "ner" in words[parent] and words[parent]["ner"] in PERSON_NER:
                        #             found = True
                        #             break
                        #         parent = words[parent]["parent"]
                        #
                        #     if found:
                        #         found_person = True
                        #         person = [words[parent]["word"]]
                        #         self.search_person_connected(words, person, parent)
                        #         if id_sent == 1132:
                        #             print person
                    # elif word["ner"] in PERSON_NER:
                    #     # if id_word > 1 and words[id_word-1]["pos"] == "IN":
                    #     #     person = []
                    #     found_person = True
                    #     person.append(word["word"])
                # elif word["word"] == "of":
                #     person = self.filter_person(words, id_word)
                #     found_person = len(person) > 0
            if found_location and found_person:
                if id_sent not in self.annotations:
                    self.annotations[id_sent] = OrderedDict()
                    self.annotations[id_sent]["location"] = location
                    self.annotations[id_sent]["person"] = person

    def create_annotations_file(self, output_file):
        file_output = open(output_file, "w")
        to_write = ""
        for id_sent, dic in self.annotations.iteritems():
            to_write += "sent" + str(id_sent) +"\t"
            for pers in dic["person"]:
                to_write += pers + " "
            to_write = to_write[:-1]
            to_write += "\t"
            to_write += "Live_In\t"
            for loc in dic["location"]:
                to_write += loc + " "
            to_write = to_write[:-1]
            to_write += "\n"
        file_output.write(to_write)
        print "Finish writing in the output annotation file in " + str(passed_time(start_time))

if __name__ == '__main__':
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    type_input = input_file.split(".")[-1]
    if type_input != "processed":
        print "The input file " + input_file + " is not in the format .processed"
        sys.exit(0)
    annotation = Annotation(input_file)
    annotation.create_annotations_file(output_file)
