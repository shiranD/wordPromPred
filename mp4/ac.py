#Copyright (c) 2015 Shiran Dudy.
#All rights reserved.

#Redistribution and use in source and binary forms are permitted
#provided that the above copyright notice and this paragraph are
#duplicated in all such forms and that any documentation,
#advertising materials, and other materials related to such
#distribution and use acknowledge that the software was developed
#by the CSLU. The name of the
#CSLU may not be used to endorse or promote products derived
#from this software without specific prior written permission.
#THIS SOFTWARE IS PROVIDED ``AS IS'' AND WITHOUT ANY EXPRESS OR
#IMPLIED WARRANTIES, INCLUDING, WITHOUT LIMITATION, THE IMPLIED
#WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.

from __future__ import division
import numpy as np
import json

def check_num(num):
    
    num = num.split("-")
    if len(num) == 2:
        units = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
          "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
          "sixteen", "seventeen", "eighteen", "nineteen", "twenty", "thirty", 
          "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]
        if num[0] in units and num[1] in units:
            return 13


def accent_ratio(x_data, y_data):
    # count how many times seen
    # count how many times emphasized
    # 0 -> 0
    # 1 -> 0.5
    # 2 -> 1
    ac_dict = {}
    pop_dict = {}
    for x, y in zip(x_data, y_data):
        for word, prom in zip(x,y):
            word = str(word[1].split("=")[1])
            try:
                pop_dict[word]
                pop_dict[word]+=1
            except:
                pop_dict[word] = 1
                ac_dict[word] = 0
                
                if prom == 0: # check if int or label
                    continue
                elif prom == 1:
                    ac_dict[word]+=0.5
                else:
                    ac_dict[word]+=1
                    
                    
    keys = pop_dict.keys()
    new_dict = {}
    for key in keys:
        new_dict[key] = ac_dict[key] / pop_dict[key]
        
    return new_dict
                    
                    
                 
def add_to_xes(train, test, ac_dict):
    new_train = []
    for words in train:
        new_sent = []
        for vector in words:
            word = str(vector[1].split("=")[1])
            ac = ac_dict[word]
            vector.append(ac)
            #vector.append("ac="+str(ac_dict[word]))
            
            new_sent.append(vector)
        new_train.append(new_sent)
    
            
    new_test = []
    for words in test:
        new_sent = []
        for vector in words:
            word = str(vector[1].split("=")[1])
            try:
                emph = ac_dict[word]
                #vector.append(emph)
                
            except:
                emph = 0.5
            ac = emph
            
            vector.append(ac)
            #vector.append("ac="+str(emph))        
            new_sent.append(vector)
        new_test.append(new_sent)    
            
    return new_train, new_test
                
                
def information_content(x_data):
    # count how many times seen
    # how many words are there
    # negative log this ratio
    # add to all the lowest value so the lowest is 0
    all_words = 0
    pop_dict = {}
    for x in x_data:
        for word in x: # how many times seen
            word = str(word[1].split("=")[1])
            try:
                pop_dict[word]
                pop_dict[word]+=1
            except:
                pop_dict[word] = 1
                
            all_words+=1
                    
    keys = pop_dict.keys()
    new_dict = {}
    for key in keys:
        new_dict[key] = int(round(-np.log(pop_dict[key] / all_words)))
    #val = min(new_dict.values())
    return new_dict


def add_to_xes1(train, test, ic_dict):
    new_train = []
    for words in train:
        new_sent = []
        for vector in words:
            word = str(vector[1].split("=")[1])
            vector.append(ic_dict[word])            
            new_sent.append(vector)
        new_train.append(new_sent)
    
            
    new_test = []
    for words in test:
        new_sent = []
        for vector in words:
            word = str(vector[1].split("=")[1])
            try:
                emph = ic_dict[word]
                #vector.append(emph)
                
            except:
                emph = 0.5                
                #pass
            vector.append(emph)
            new_sent.append(vector)
        new_test.append(new_sent)    
            
    return new_train, new_test


def add_to_xes2(train, test, path):
    
    for line in open(path,"r").readlines():
        ic_dict = json.loads(unicode(line))
        
    new_train = []
    for words in train:
        new_sent = []
        for vector in words:
            word = str(vector[1].split("=")[1])
            try:
                emph = ic_dict[word]                
            except:
                #print word
                frequency = 0
                emph = -int(round(np.log(1 + frequency)))
            vector.append(emph)
            #vector.append("ic="+str(emph))
            new_sent.append(vector)
        new_train.append(new_sent)     
        
        
    new_test = []
    for words in test:
        new_sent = []
        for vector in words:
            word = str(vector[1].split("=")[1])
            try:
                emph = ic_dict[word]                
            except:
                frequency = 0
                emph = -int(round(np.log(1 + frequency))) 
            vector.append(emph)
            #vector.append("ic="+str(emph))
            new_sent.append(vector)
        new_test.append(new_sent)
        
    return new_train, new_test
