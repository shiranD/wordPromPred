import os
from nltk.corpus import cmudict
from nltk.tag import HunposTagger
from nltk.tag.mapping import map_tag
import yaml
import json
from random import randint
import shutil
import copy
from collections import OrderedDict
import re

SOURCE = 'en-ptb'


def pre_process_line(sentence):
    """ remove punctuation and convert symbols to words"""

    sentence = sentence.replace("...\n", "")
    sentence = sentence.replace(".\n", "")
    sentence = sentence.replace("''\n", "")
    sentence = sentence.replace("'\n", "")
    sentence = sentence.replace(",\n", "")
    sentence = sentence.replace(":\n", "")
    sentence = sentence.replace("]\n", "")
    sentence = sentence.replace("--\n", "")
    sentence = sentence.replace("``\n", "")
    sentence = sentence.replace(" . ", " ")
    sentence = sentence.replace(";", "")
    sentence = sentence.replace(" , ", " ")
    sentence = sentence.replace("!", "")
    sentence = sentence.replace("?", "")
    sentence = sentence.replace(" ' ", " ")
    sentence = sentence.replace(" '' ", " ")
    sentence = sentence.replace(" : ", " ")
    sentence = sentence.replace(" -- ", " ")
    sentence = sentence.replace("-- ", " ")
    sentence = sentence.replace("'' ", " ")
    sentence = sentence.replace("' ", " ")
    sentence = sentence.replace(" `` ", " ")
    sentence = sentence.replace("`` ", " ")
    sentence = sentence.replace(" ` ", " ")
    sentence = sentence.replace("` ", " ")
    sentence = sentence.replace(" - ", " ")
    sentence = sentence.replace(" [ ", " ")
    sentence = sentence.replace(" ] ", " ")
    sentence = sentence.replace(" ( ", " ")
    sentence = sentence.replace(" ) ", " ")
    sentence = sentence.replace("( ", " ")
    sentence = sentence.replace("[ ", " ")
    sentence = sentence.replace("- ", " ")
    sentence = sentence.replace(" $ ", " dollars ")
    sentence = sentence.replace("$ ", " dollars ")
    sentence = sentence.replace("%", "percent")
    sentence = sentence.replace(" & ", " and ")
    sentence = sentence.replace(" # ", " number ")
    sentence = sentence.replace("# ", " number ")
    sentence = sentence.replace("@ ", " at ")
    sentence = sentence.replace(" @ ", " at ")
    sentence = sentence.replace("= ", " equals ")
    sentence = sentence.replace(" = ", " equals ")
    return sentence.replace("...", "")


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


def featurize(sentence, idnum, pat):
    """ construct json file per sentence s.t. every word is described by:
    its tag, its collapsed tag (according to NLTK 3.0), a function
    word (bool), negation (bool), vowels, num of syllables,
    and current past and future of words in terms of the
    nucleuos and level of prominence """

    processed_sentence = pre_process_line(sentence)
    word_tag = hpt.tag(processed_sentence.split())  # tag all sentence
    last = len(word_tag) - 1
    past_nuc = ''
    past_kind = ''
    number_pattern = re.compile(r"(\d+)?[.,-]?(\\/)?\d+(th)?('s)?['s]?(\w+)?")
    hiphend_pattern_num_word_mix = re.compile(r"(\w+(.\w+)?(\w+)?)-\w+")
    filename = pat + '/' + str(idnum)
    with open(str(filename), 'a') as datafile:  # open json file

        for (i, (word, tag)) in enumerate(word_tag):
            current_word = []

            # if word is a contraction (no "'s")
            if word in ["'d", "'ll", "'n'", "'re", "'ve", "n't"]:
                past_word[0][1] = past_word[0][1] + word
                phns = d[past_word[0][1].lower()][0]
                past_word[4][1] = bool(word in negation)               
                sylls, num_syll, nuc, kind = syll_detector(phns)
                past_word[5][1] = sylls
                past_word[6][1] = num_syll
                past_word[7][1] = nuc
                past_word[8][1] = kind
                continue

            if re.findall(number_pattern, word):  # check if number
                word = 'five'
                tag = '*NUMBER*'

            current_word.append(['word', word.lower()])
            current_word.append(('tag', tag))
            current_word.append(
                ('collps_tag', map_tag(SOURCE, target='universal',
                                       source_tag=tag)))
            current_word.append(('function', bool(word in function)))
            current_word.append(['negation', bool(word in negation)])
            try:
                phns = d[word.lower()][0]
            except:
                # hyphen seperated
                if re.findall(hiphend_pattern_num_word_mix, word):
                    phns = []
                    for w in word.split('-'):
                        try:
                            ph = d[w.lower()][0]
                            phns.extend(ph)
                        except:
                            # and there's a number
                            if re.findall(number_pattern, word):
                                w = 'five'
                                ph = d[w.lower()][0]
                                phns.extend(ph)
                else:
                    if word == ",":
                        print 'h'
                    print word

                    f.write(word)
                    f.write('\n')  # find if it is a number or dot or pound
                    word = 'name'  # unrecognized word or pattern
                    current_word[0][1] = word
                    phns = d[word.lower()][0]

            sylls, num_syll, nuc, kind = syll_detector(phns)
            current_word.append(['vowels', sylls])
            current_word.append(['num_sylls', num_syll])
            current_word.append(['nuc', nuc])
            current_word.append(['nuc_kind', kind])

            if i > 0:  # if not first word
                past_word.append(('right_nuc', nuc))
                past_word.append(('right_nuc_kind', kind))

                # copy past_word to json
                json.dump(OrderedDict(past_word), file, indent=4)
                current_word.append(('left_nuc', past_nuc))
                current_word.append(('left_nuc_kind', past_kind))
            # after updating current_word, current nuc becomes past_nuc
            past_nuc = nuc
            past_kind = kind

            if i == 0:
                current_word.append(('left_nuc', 'None'))

            if i == last:
                current_word.append(('right_nuc', 'None'))
                # copy final_word to jason
                json.dump(OrderedDict(current_word), file, indent=4)

            past_word = copy.deepcopy(current_word)  # keep past dict


yml_path = '../config/config.yml'
with open(yml_path, 'r') as f1:  # load config file
    conf = yaml.load(f1)

with open(conf['function'], 'r') as f1:  # load function words
    words = f1.read()
    function = words.split('\n')


with open(conf['negation'], 'r') as f1:  # load negation words
    words = f1.read()
    negation = words.split('\n')

hpt = HunposTagger(conf['tagger'], conf['tagexe'])  # load tagger
d = cmudict.dict()  # load cmudict

with open(conf['data']) as f1:  # load sentence by sentence
    f = open('unseen', 'w')
    lotteried = randint(10000, 100000)  # generate 6 num code
    path = '../out_' + str(lotteried)  # path to output file

    if not os.path.exists(path):
        os.makedirs(path)

    shutil.copy2(yml_path, path)  # copy config file to output file
    j = 0
    for line in f1.readlines():  # mpi TBD
        feats = featurize(line, j, path)
        j += 1
