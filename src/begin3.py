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

def syll_detector(phns):
    one = [];onekind = []
    zero = []; zerokind = []
    two = []; twokind = []
    for phn in phns:
        if '1' in phn: 
            one.append(phn)
            onekind.append('1')
        if '2' in phn:
            two.append(phn)
            twokind.append('2')
        if '0' in phn:
            zero.append(phn)
            zerokind.append('3')
            
    all_syll = one+two+zero
    all_kinds = onekind+twokind+zerokind
    return all_syll, len(all_syll), all_syll[0], all_kinds[0]

def featurize(line, idnum, pat):
    
    word_tag = hpt.tag(line.split()) # tag all sentence
    last = len(word_tag) - 1
    past_nuc = ''
    past_kind = ''
    
    filename = pat+'/'+str(idnum)   
    with open(str(filename), 'a') as file: #open json file
        
        for (i,(word,tag)) in enumerate(word_tag):
            current_word = []
            current_word.append(('word',word.lower()))
            current_word.append(('tag',tag))
            current_word.append(('collps_tag',map_tag(source='en-ptb',target='universal', source_tag=tag))) # source = 'en-ptb' is for wsj [TBD no wsj?]
            current_word.append(('function',bool(word in function)))
            current_word.append(('negation',bool(word in negation)))
            try: 
                phns = d[word.lower()][0]
            except:
                f.write(word)
                f.write('\n') #find if it is a number or dot or pound                
                continue
            sylls, num_syll, nuc, kind = syll_detector(phns)
            current_word.append(('sylls', sylls))             
            current_word.append(('num_sylls', num_syll))
            current_word.append(('nuc', nuc))
            current_word.append(('nuc_kind', kind))
            
            
            if i > 0: # if not first word
                past_word.append(('right_nuc',nuc)) 
                past_word.append(('right_nuc_kind',kind)) 
                
                json.dump(OrderedDict(past_word), file, indent=4) #copy past_word to json
                current_word.append(('left_nuc',past_nuc))
                current_word.append(('left_nuc_kind',past_kind))
            past_nuc = nuc # after updating current_word, current nuc becomes past_nuc
            past_kind = kind
                        
            if i == 0:
                current_word.append(('left_nuc','None'))
                
            if i == last:
                current_word.append(('right_nuc','None'))
                json.dump(OrderedDict(current_word), file, indent=4) #copy final_word to jason
            
            past_word = copy.deepcopy(current_word) # keep past dict
            
           

yml_path = '../config/config.yml' 
with open(yml_path, 'r') as f1: # load config file
    conf = yaml.load(f1)
    
with open(conf['function'],'r') as f1: # load function words
    words = f1.read()
    function = words.split('\n') 
    
    
with open(conf['negation'],'r') as f1: # load negation words
    words = f1.read()
    negation = words.split('\n')     
    
hpt = HunposTagger(conf['tagger'],conf['tagexe']) # load tagger
d = cmudict.dict() # load cmudict

with open(conf['data']) as f1: #load sentence by sentence
    f = open('unseen','w')    
    lotteried = randint(10000,100000) # generate 6 num code
    path = '../out_'+str(lotteried) # path to output file
    
    if not os.path.exists(path):
        os.makedirs(path) 
        
    shutil.copy2(yml_path, path) # copy config file to output file
    j = 0
    for line in f1.readlines():# mpi TBD
        feats = featurize(line,j,path)
        j+=1
        
