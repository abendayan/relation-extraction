import json
from collections import OrderedDict
from nltk.corpus import wordnet as wn
import pdb
import random
import spacy
nlp = spacy.load('en')

countriesJson = json.load(open('countries.json'))
usJson = json.load(open('us.json'))
citiesJson = json.load(open('cities.json'))
states = []

for s in usJson:
    states.append(usJson[s].lower().replace(" ", "-"))
countries = []

for c in countriesJson:
    countries.append(c["name"].lower().replace(" ", "-"))

countries.append("u.s.")
cities = {}

for c in citiesJson:
    cities[c["name"].lower().replace(" ", "-")] = 1

LOCATIONS = [ 'LOCATION' ]
PERSON = ['PERSON']
def build_corpus(sentences):
    sentences_dic = {}
    for sentence in sentences:
        if sentence != "":
            id_number = int(sentence.split("\t")[0].replace("sent", ""))
            parsed = nlp(unicode(sentence.split("\t")[1]))
            sentences_dic[id_number] = OrderedDict()
            sentences_dic[id_number]["text"] = sentence.split("\t")[1]
            sentences_dic[id_number]["words"] = {}
            # sentenceData = []
            # sentenceDic = {}

            for i, word in enumerate(parsed):
                head_id = word.head.i + 1  # we want ids to be 1 based
                if word == word.head:  # and the ROOT to be 0.
                    assert (word.dep_ == "ROOT"), word.dep_
                    head_id = 0  # root

                words = {
                    "id": word.i + 1,
                    "word": word.text,
                    "lemma": word.lemma_,
                    "pos": word.pos_,
                    "tag": word.tag_,
                    "parent": head_id,
                    "dependency": word.dep_,
                    "bio": word.ent_iob_,
                    "ner": word.ent_type_
                }
                sentences_dic[id_number]["words"][words["id"]] = words
        #     guh
    # for word in words:
    #     if word != "":
    #         sentence.append(word)
    #     else:
    #         if sentence != []:
    #             build_sentence(sentence, sentences)
    #         sentence = []
    return sentences_dic

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
        words["id"] = int(words_ent[0])
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

def chunk_phrase(chunks):
    phrase = ""
    for chunk in chunks:
        if chunk['word'] in ['.', '-']:
            phrase = phrase[:-1] + chunk['word']
        else:
            phrase += chunk['word'] + ' '
    return phrase[:-1]

def extract_chunks(words):
    i = 0
    chunks = []
    chunk = []
    previous = None
    for id, word in words.iteritems():
        if word['bio'] in {'O','B'}:
            # if word['bio'] != '0' and id-1 in words and words[id-1]["parent"] == id and words[id-1]["tag"] == "PROPN":
            #     chunk.append(relevent_inf(words[id-1]))
            if word['bio'] == '0' and word['dep'] == 'compound':
                chunk.append(word)
            if chunk:
                chunks.append(chunk)
            chunk = []
            if word['bio'] == '0' and word['dep'] == 'compound':
                chunk.append(word)
        if word['bio'] in {'I','B'}:
            chunk.append(word)
        previous = word
        i +=1
    return chunks

def find_ngrams(input_list, n):
    ngram = zip(*[input_list[i:] for i in range(n)])
    ngram_concat = []
    for gram in ngram:
        to_add = ""
        for elem in gram:
            to_add += elem
        ngram_concat.append(to_add)
    return ngram_concat

def chunk_pos(chunks, pos):
    for chunk in chunks:
        if pos not in chunk["pos"]:
            return False
    return True

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

def in_gazette(word):
    word = word.lower().replace(" ", "-")
    return word.lower() in countries or word.lower() in states or word.lower() in cities

def is_country(word):
    word = word.lower().replace(" ", "-")
    return word in countries

def is_city(word):
    word = word.lower().replace(" ", "-")
    return word in cities

def is_state(word):
    word = word.lower().replace(" ", "-")
    return word in states
def entity_to_loc(entity):
    # syns = wn.synsets(entity["word"], 'n')
    # without_last = entity["lemma"][:-1].replace(" ", "-")
    # word = entity["lemma"].replace(" ", "-")
    # if not in_gazette(word):
    #     if without_last in countries or without_last in cities or without_last in states:
    #         return entity['ner']
    # if len(syns) > 0:
    #     list_sim = [lemma.name() for synset in syns[0].hyponyms() for lemma in synset.lemmas()]
    #     for sim in list_sim:
    #         if sim in countries or sim in cities or sim in states:
    #             return "LOCATION"

    if entity["ner"] in LOCATIONS :
    # if entity["ner"] in LOCATIONS or in_gazette(word):
        return "LOCATION"
    return entity["ner"]

def entity_to_pers(entity):
    if entity in PERSON:
        entity = "PERSON"
    return entity

def name_or_entity(word):
    if word["pos"].startswith("NN"):
        return "NN"
    return word["pos"]

class Features:
    def __init__(self, m1, m2, sentence):
        self.m1 = m1
        self.m2 = m2
        self.feat = []
        self.build_features(sentence)
    def build_features(self, sentence):
        # entity based features
        # entity type 1
        self.feat.append(self.m1[-1]["ner"])
        self.feat.append(entity_to_pers(self.m1[-1]["ner"]))
        # entity 1 head
        self.feat.append(self.m1[-1]['word'])
        # entity type 2
        self.feat.append(self.m2[-1]["ner"])
        self.feat.append(entity_to_loc(self.m2[-1]))
        # entity 2 head
        self.feat.append(self.m2[-1]['word'])
        # concatenate types
        self.feat.append(self.m1[-1]["ner"] + self.m2[-1]["ner"])
        # concatenate head
        # self.feat.append(self.m1[-1]['word'] + self.m2[-1]['word'])

        for word in self.m1:
            self.feat.append(word["pos"])
        for word in self.m2:
            self.feat.append(word["pos"])
        # word based features
        start = False
        before1 = None
        before2 = None
        after1 = None
        after2 = None
        syntact_chunk = []
        for id, word in sentence.iteritems():
            if word == self.m2[0]:
                start = False
                if id-1 in sentence:
                    before2 = sentence[id-1]["word"]
            if word == self.m2[-1]:
                if id+1 in sentence:
                    after2 = sentence[id+1]["word"]
                break
            if start:
                self.feat.append("Between+"+word["word"])
                syntact_chunk.append(word["pos"])
            if word == self.m1[0]:
                if id-1 in sentence:
                    before1 = sentence[id-1]["word"]
            if word == self.m1[-1]:
                if id+1 in sentence:
                    after1 = sentence[id+1]["word"]
                start = True
        for syntact in syntact_chunk:
            self.feat.append("Base"+syntact)
        # word before entity 1
        if before1 is None:
            self.feat.append("BeforeEnt1Start")
        else:
            self.feat.append("BeforeEnt1"+before1)
        if before2 is None:
            self.feat.append("BeforeEnt2Start")
        else:
            self.feat.append("BeforeEnt2"+before2)

        if after1 is None:
            self.feat.append("AfterEnt1End")
        else:
            self.feat.append("AfterEnt1"+after1)
        if after2 is None:
            self.feat.append("AfterEnt2End")
        else:
            self.feat.append("AfterEnt2"+after2)

        # # entity level
        self.feat.append(name_or_entity(self.m1[-1]))
        self.feat.append(name_or_entity(self.m2[-1]))

        # synonyms
        syns = wn.synsets(chunk_phrase(self.m1), 'n')
        if len(syns) > 0:
            list_sim = [lemma.name() for synset in syns[0].hyponyms() for lemma in synset.lemmas()]
            for sim in list_sim:
                self.feat.append(sim)
        syns = wn.synsets(chunk_phrase(self.m2), 'n')
        if len(syns) > 0:
            list_sim = [lemma.name() for synset in syns[0].hyponyms() for lemma in synset.lemmas()]
            for sim in list_sim:
                self.feat.append(sim)
        dep = self.m1[0]["parent"]
        while dep != 0 and dep != self.m2[-1]["id"]:
            self.feat.append(sentence[dep]["word"])
            dep = sentence[dep]["parent"]
        dep = self.m2[-1]["parent"]
        while dep != 0 and dep != self.m1[0]["id"]:
            self.feat.append(sentence[dep]["word"])
            dep = sentence[dep]["parent"]

        for word in self.m1:
            if is_city(word["word"]):
                self.feat.append("CityLeft"+word["word"])
        #     else:
        #         self.feat.append("City_"+word["word"]+"_0")
            if is_state(word["word"]):
                self.feat.append("StateLeft"+word["word"])
        #     else:
        #         self.feat.append("State_"+word["word"]+"_0")
            if is_country(word["word"]):
                self.feat.append("CountryLeft"+word["word"])
        #     else:
        #         self.feat.append("Country_"+word["word"]+"_0")
        #
        for word in self.m2:
            if is_city(word["word"]):
                self.feat.append("CityRight"+word["word"])
            # else:
            #     self.feat.append("City_"+word["word"]+"_0")
            if is_state(word["word"]):
                self.feat.append("StateRight"+word["word"])
            # else:
            #     self.feat.append("State_"+word["word"]+"_0")
            if is_country(word["word"]):
                self.feat.append("CountryRight"+word["word"])
            # else:
                # self.feat.append("Country_"+word["word"]+"_0")

        if random.randint(1, 100) == 1:
            self.feat.append("UNK")
