from nltk.corpus import cmudict
from nltk.tag import HunposTagger
from nltk.tag.mapping import tagset_mapping, map_tag
import yaml

def tupl(*params): # make the tuple
    num = 6
    if len(params) == num:# confirm it contains exactly 6 params
        return params
    else:
        raise 'error'
        #d = tupl(1,'we','r')
    

def featurize(line):
    word_tag = hpt.tag(line.split()) # tag all
    
    for (word,tag) in word_tag:
        a = map_tag(source='en-ptb',target='universal', source_tag=tag) # source = 'en-ptb' is for wsj [TBD no wsj?]
        x if word in function else y
        x if word in negation else y
        len(d[word])
        
        
        
    
#open config file
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
    # open jason
    # generate 6 num code
    for line in f1.readlines():# mpi TBD
        feats = featurize(line)
        #write feats to json
    #close json

# write config param with key of 6 num code
    
#write to json