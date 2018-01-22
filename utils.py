import json
from collections import OrderedDict
from nltk.corpus import wordnet as wn
import pdb
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
LOCATIONS = [ 'GSP', 'FACILITY', 'LOC', 'NORP', 'ORG']
PERSON = ['PERSON']
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
        if word["pos"] not in { 'CD' }:
            if word['bio'] in {'O','B'}:
                if chunk:
                    chunks.append(chunk)
                chunk = []
                # if word['dep'] in {'compound'}:
                #     chunk.append(word)
            # if word['bio'] in {'I','B'} or (previous and previous["lemma"] in { 'of' }):
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
    return word.lower() in countries or word.lower() in states or word.lower() in cities

def entity_to_loc(entity):
    # print entity["word"]
    syns = wn.synsets(entity["word"], 'n')
    if len(syns) > 0:
        # print syns
        # print entity["word"]
        # hypos = lambda s:s.hyponyms()

        list_sim = [lemma.name() for synset in syns[0].hyponyms() for lemma in synset.lemmas()]
        for sim in list_sim:
            if sim in countries or sim in cities or sim in states:
                return "LOCATION"
        # ghujio
    if entity["ner"] in LOCATIONS or entity["word"].lower() in countries or entity["word"].lower() in states or entity["word"].lower() in cities:
        return "LOCATION"
    return entity["ner"]

def entity_to_pers(entity):
    if entity in PERSON:
        entity = "PERSON"
    return entity

class Features:
    def __init__(self, m1, m2, sentence):
        self.m1 = m1
        self.m2 = m2
        self.feat = []
        self.build_features(sentence)
    def build_features(self, sentence):
        # m1 : last word
        # m2 : last word
        # bags of words & bigrams
        # word left to m1
        # word right to m1
        # word left to m2
        # word right to m2
        self.feat.append(chunk_phrase(self.m1))
        self.feat.append(chunk_phrase(self.m1).lower())
        self.feat.append(chunk_phrase(self.m2))
        self.feat.append(chunk_phrase(self.m2).lower())
        self.feat.append(chunk_phrase(self.m1)+chunk_phrase(self.m2))

        self.feat.append(self.m1[-1]['word'])
        self.feat.append(self.m1[-1]['word'].lower())
        self.feat.append(self.m2[-1]['word'])
        self.feat.append(self.m2[-1]['word'].lower())
        self.feat.append(self.m1[-1]['word'] + self.m2[-1]['word'])
        self.feat.append(self.m1[-1]['word'].lower() + self.m2[-1]['word'].lower())
        bags_bigrams = []
        bags = []
        if len(self.m1) > 1:
            for word in self.m1:
                bags.append(word['word'])
                bags.append(word['word'].lower())
        bags_bigrams.extend(bags)
        # bags_bigrams.extend(find_ngrams(bags, 2))
        bags = []
        if len(self.m2) > 1:
            for word in self.m2:
                bags.append(word['word'])
                bags.append(word['word'].lower())
        bags_bigrams.extend(bags)
        # bags_bigrams.extend(find_ngrams(bags, 2))
        self.feat.extend(bags_bigrams)
        m1 = self.m1[0]
        m2 = self.m2[0]
        if m1["id"]-1 in sentence:
            self.feat.append(sentence[m1["id"]-1]["word"])
        else:
            self.feat.append("Start")
        if m1["id"]+1 in sentence:
            self.feat.append(sentence[m1["id"]+1]["word"])
        else:
            self.feat.append("End")
        if m2["id"]-1 in sentence:
            self.feat.append(sentence[m2["id"]-1]["word"])
        else:
            self.feat.append("Start")
        if m2["id"]+1 in sentence:
            self.feat.append(sentence[m2["id"]+1]["word"])
        else:
            self.feat.append("End")
        entity_left = entity_to_pers(self.m1[-1]["ner"])
        # # if entity_left != "PERSON":
        # #     entity_left = entity_to_loc(self.m1[-1])
        entity_right = entity_to_loc(self.m2[-1])
        self.feat.append(entity_left)
        self.feat.append(entity_right)
        for m2 in self.m2:
            self.feat.append(m2["word"] + str(in_gazette(m2["word"])))
        for m1 in self.m1:
            self.feat.append(m1["word"] + str(in_gazette(m1["word"])))
        self.feat.append(entity_left + "-" + entity_right)
        self.feat.append(chunk_phrase(self.m1) + str(chunk_pos(self.m1, "NN")))
        self.feat.append(chunk_phrase(self.m2) + str(chunk_pos(self.m2, "NN")))
        self.feat.append(self.m1[-1]["tag"])
        self.feat.append(self.m2[-1]["tag"])
        start = False
        between = []
        pattern = []
        for id, word in sentence.iteritems():
            if word["word"] in {"home", "live", "of"}:
                pattern.append(word["word"])
            if word == self.m2[0]:
                break
            if start:
                between.append(word["word"])
            if not start and word == self.m1[-1]:
                start = True
        start = False
        between.extend(find_ngrams(between, 2))
        between.extend(find_ngrams(between, 3))
        self.feat.extend(between)
        self.feat.extend(pattern)
        for id, word in sentence.iteritems():
            if word == self.m2[0]:
                self.feat.append(word["pos"])
                break
            if start:
                self.feat.append(word["pos"])
            if not start and word == self.m1[-1]:
                start = True
                self.feat.append(word["pos"])

        syns = wn.synsets(chunk_phrase(self.m1), 'n')
        for ss in syns:
            for lema in ss.lemma_names():
                self.feat.append(lema)
                self.feat.append(lema.capitalize())
        syns = wn.synsets(chunk_phrase(self.m2), 'n')
        for ss in syns:
            for lema in ss.lemma_names():
                self.feat.append(lema)
                self.feat.append(lema.capitalize())
