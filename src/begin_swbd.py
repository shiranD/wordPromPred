import os
from os import walk
from nltk.corpus import cmudict
from nltk.tag.mapping import map_tag
import yaml
import json
from random import randint
import shutil
import copy
from collections import OrderedDict
import re
import ast

Source = 'en-ptb'


def find(string, ch):
    """list the indecies of '{' char"""
    idx = []
    for i, ltr in enumerate(string):
        if ltr == ch:
            idx.append(i)
    return idx


def dict_the_json(out, jsonfiles):
    """parse json objects to dict representation"""
    
    for jsonfile in jsonfiles:
        json_string = out+'/'+jsonfile
        with open(json_string) as fjson:
            yield json.load(fjson)


def syll_detector(phns):
    """ given the phonemes of a word, determine the vowels, how many vowels, 
    which is the prominent, its level of prominence """

    one = []
    onekind = []
    two = []
    twokind = []
    three = []
    threekind = []
    four = []
    fourkind = []
    for phn in phns:
        if '1' in phn:
            # tense
            if phn[:-1] in ['ER', 'IY', 'EY', 'OW', 'UW', 'AY', 'OY', 'AW']:
                one.append(phn)
                onekind.append('1')
            if phn[:-1] in ['IH', 'EH', 'AE', 'AA', 'AH', 'UH', 'AO']:  # lax
                two.append(phn)
                twokind.append('2')
        if '2' in phn:
            three.append(phn)
            threekind.append('3')
        if '0' in phn:
            four.append(phn)
            fourkind.append('4')

    all_syll = one + two + three + four
    all_kinds = onekind + twokind + threekind + fourkind
    return all_syll, len(all_syll), all_syll[0], all_kinds[0]


def featurize(indir, pat, jsons):
    """ construct json file per sentence s.t. every word is described by: 
    its tag, its collapsed tag (according to NLTK 3.0), a function 
    word (bool), negation (bool), vowels, num of syllables, and current
    past and future of words in terms of the nucleuos and level of 
    prominence """
    
    outdir = pat + '/' + indir.rsplit("/", 1)[-1]    
    if not os.path.exists(outdir):
        os.makedirs(outdir)    
    past_nuc = ''
    past_kind = ''
    number_pattern = re.compile("(\d+)?[.,-]?(\\/)?\d+(th)?('s)?['s]?(\w+)?")
    hiphend_pattern_num_word_mix = re.compile("(\w+(.\w+)?(\w+)?)-\w+")
    past_word = []
    last = len(jsons)
    first_dumped = 0 # since not necessarily the first word is dumped
    for (i, terminal) in enumerate(dict_the_json(indir, jsons)):

        word = str(terminal["word"].lower())
        subword = str(terminal["subword"].lower())
        if word != subword:
            # print word, subword
            pass

        try: # if "repair" or not exist keeps going 
            if terminal["disf_stat"] == "reparandum":
                continue
        except:
            pass

        current_word = []

        # if find list of shortcut verb suffix (no "'s")
        if past_word and (word in ["'d", "'ll", "'n'", "'re", "'ve",\
                                   "n't", "'m"]
                          or (past_word[0][1] + word == subword and \
                              subword in ["he's", "she's", "it's", "that's", "what's"])
                          or (past_word[0][1] + word == subword and word != "'s")):
            past_word[0][1] = past_word[0][1] + word
            try:
                phns = d[past_word[0][1].lower()][0]
            except:
                # print past_word[0][1].lower()
                phn1 = d[past_word[0][1][:-len(word)]][0]
                phn2 = d[str(word)][0]
                phns = phn1 + phn2

            sylls, num_syll, nuc, kind = syll_detector(phns)
            for k in xrange(7): # max sylls
                try:
                    current_word.append((k, sylls[k]))
                except:
                    current_word.append((k, "NA"))  
                    
            #past_word[5][1] = sylls
            #past_word[6][1] = num_syll
            #past_word[7][1] = nuc
            #past_word[8][1] = kind
            #past_word[12][1] = num_syll
            past_word[12][1] = nuc
            past_word[13][1] = kind
            continue


        current_word.append(['word', word])
        current_word.append(('tag', terminal["tag"]))
        current_word.append(
            ('collps_tag', map_tag(Source, target='universal',\
                                   source_tag=terminal["tag"])))
        
        current_word.append(('function', bool(word) in function))
        current_word.append(('negation', bool(word) in negation))
        try:
            phns = d[word][0]
        except:
            # hiphen seperated
            if re.findall(hiphend_pattern_num_word_mix, word):
                phns = []
                for w in word.split('-'):
                    try:
                        phn = d[w.lower()][0]
                        phns.extend(phn)
                    except:
                        # and there's a number
                        if re.findall(number_pattern, word):
                            w = 'five'
                            phn = d[w.lower()][0]
                            phns.extend(phn)
            else:
                if word == ",":
                    print 'h'
                # print word

                f.write(word)
                f.write('\n')  # find if it is a number or dot or pound
                word = 'name'  # unrecognized word or pattern
                current_word[0][1] = word
                phns = d[word.lower()][0]

        sylls, num_syll, nuc, kind = syll_detector(phns)
        for k in xrange(7): # max sylls
            try:
                current_word.append((k, sylls[k]))
            except:
                current_word.append((k, "NA"))   
                
        current_word.append(['nuc', nuc])
        current_word.append(['nuc_kind', kind])
        try:  # dialact
            current_word.append(("dialAct", terminal["dialAct:niteType"]))
            current_word.append(("seq", terminal["dialAct:id"]))          
        except:
            current_word.append(("dialAct", "no"))
        try:  # kontrast
            current_word.append(
                ("kontrast level", terminal["kontrast:level"]))
            current_word.append(
                ("kontrast type", terminal["kontrast:type"]))
        except:
            current_word.append(
                ("kontrast level", "no"))
            current_word.append(
                ("kontrast type", "no"))            
        try:  # phrases
            current_word.append(('phrases', terminal["phrases:type"]))
        except:
            current_word.append(('phrases', "no"))

        try:  # accents
            current_word.append(
                ('accents_strength', terminal["accents:strength"]))
        except:
            pass

        if first_dumped and i!=last:  # if not first dumped word 
            past_word.append(('right_nuc', nuc))
            past_word.append(('right_nuc_kind', kind))

            # copy past_word to json
            with open(outdir+'/'+past_id, 'w') as fjson:
                json.dump(OrderedDict(past_word), fjson, indent=4)
            current_word.append(('left_nuc', past_nuc))
            current_word.append(('left_nuc_kind', past_kind))
        # after updating current_word, current nuc becomes past_nuc
        past_nuc = nuc
        past_kind = kind

        if not first_dumped:
            current_word.append(('left_nuc', 'None'))
            first_dumped = 1

        if i == last:
            current_word.append(('right_nuc', 'None'))
            # copy final_word to jason
            with open(outdir+'/'+past_id, 'w') as fjson:
                json.dump(OrderedDict(current_word), fjson, indent=4)            

        past_word = copy.deepcopy(current_word)  # keep past dict
        past_id = terminal["id"]


yml_path = '../config/config_swbd.yml'
with open(yml_path, 'r') as f1:  # load config file
    conf = yaml.load(f1)

with open(conf['function'], 'r') as f1:  # load function words
    words = f1.read()
    function = words.split('\n')


with open(conf['negation'], 'r') as f1:  # load negation words
    words = f1.read()
    negation = words.split('\n')

d = cmudict.dict()  # load cmudict

f = open('unseen_swbd', 'w')
lotteried = randint(10000, 100000)  # generate 6 num code
path = '../out_' + str(lotteried)  # path to output file

if not os.path.exists(path):
    os.makedirs(path)

shutil.copy2(yml_path, path)  # copy config file to output file
path2files = conf['data']
with open(path2files) as filenames:
    for dirname in filenames.readlines():
        for (dirpath, dnames, fnames) in walk(dirname[:-1]):
            c = [ int(t) for t in fnames]            
            fnames = [str(t) for t in sorted(c)]
            break        
        featurize(dirname[:-1], path,fnames)
