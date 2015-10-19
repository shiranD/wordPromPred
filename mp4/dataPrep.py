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

from os import walk
import json
from random import sample, shuffle, seed

# prepare the data 

def load_datap(datapath):
    """load data"""

    X_data = []
    y_data = []
    #h=0
    last_dialAct = "n" # do it by dialect ID    
    for (i, supdir) in enumerate(walk(datapath)):
        prefix = supdir[0] + '/'
        suffixes = supdir[2]
        if suffixes == [".DS_Store","config_swbd.yml"]:
            continue
        
        X_seq = []
        y_seq = []
        feat = []

        for suffix in suffixes:
            jfilename = prefix + suffix
            with open(jfilename) as fjson:
                
                jdict = json.load(fjson)                
                
                if jdict["dialAct"]=="no":
                    continue  
                if jdict["seq"]!=last_dialAct:
                    if feat:
                        feat.append("ultimate_w")
                    #h+=1
                    #if h ==78:
                        #print h
                    X_data.append(X_seq)
                    y_data.append(y_seq)
                    X_seq = []
                    y_seq = []                    
                    g=0
                    
                else:
                    g+=1                   
                last_dialAct=jdict["seq"]                
                
                # read json as dict
                feat = []
                feat.append("*bias*")
                 
                feat.append("word="+jdict["word"])
                feat.append("tag="+jdict["tag"])
                feat.append("cltag="+jdict["collps_tag"])
                feat.append("func="+str(jdict["function"]))
                feat.append("neg="+str(jdict["negation"]))
                feat.append("0="+jdict["0"])
                feat.append("1="+jdict["1"])
                feat.append("2="+jdict["2"])
                feat.append("3="+jdict["3"])
                feat.append("4="+jdict["4"])
                feat.append("5="+jdict["5"])
                feat.append("6="+jdict["6"])
                feat.append("nuc="+jdict["nuc"])
                feat.append("nuc_kind="+jdict["nuc_kind"])
                feat.append("left_nuc="+jdict["left_nuc"])
                feat.append("right_nuc="+jdict["right_nuc"])
                feat.append("right_kind="+jdict["right_nuc_kind"])
                feat.append("dialAct="+jdict["dialAct"])
                feat.append("phrases="+jdict["phrases"])
                feat.append("kon_type="+jdict["kontrast type"])
                feat.append("kon_level="+jdict["kontrast level"])
                
                if g==0:
                    feat.append("initial_w")
                if g==1:
                    feat.append("second_w")                
                                

                try:  # remove Y values from dict to create Y
                    accent = jdict["accents_strength"]
                    del jdict["accents_strength"]
                except:
                    accent = "0"
                    
                X_seq.append(feat)
                #if len(X_seq)==13:
                    #print "13"
                
                # labels cannot be "0"
                if accent == "full":
                    y_seq.append("0")
                elif accent == "weak":
                    y_seq.append("1")
                else:
                    y_seq.append("2")

                
        X_data.append(X_seq)
        y_data.append(y_seq) 
               
        
    X = []
    Y = []
    for x,y in zip(X_data,y_data):
        if not x:
            continue
        else:
            assert len(x)==len(y)
            X.append(x)
            Y.append(y)            
    return X, Y


def load_data(datapath):
    """load data"""

    X_data = []
    y_data = []

    last_dialAct = "n" # do it by dialect ID    
    for (i, supdir) in enumerate(walk(datapath)):
        prefix = supdir[0] + '/'
        suffixes = supdir[2]
        if suffixes == [".DS_Store","config_swbd.yml"]:
            continue
        
        X_seq = []
        y_seq = []
        feat = []

        for suffix in suffixes:
            jfilename = prefix + suffix
            with open(jfilename) as fjson:
                
                jdict = json.load(fjson)                
                
                if jdict["dialAct"]=="no":
                    continue  
                if jdict["seq"]!=last_dialAct:
                    if feat:
                        feat.append("ultimate_w")
                    X_data.append(X_seq)
                    y_data.append(y_seq)
                    X_seq = []
                    y_seq = []                    
                    g=0
                    
                else:
                    g+=1
                    feat.append("between") 
                last_dialAct=jdict["seq"]                
                
                # read json as dict
                feat = []
                feat.append("*bias*")
                 
                feat.append("word="+jdict["word"])
                feat.append("tag="+jdict["tag"])
                #feat.append("cltag="+jdict["collps_tag"])
                #feat.append("func="+str(jdict["function"]))
                #feat.append("neg="+str(jdict["negation"]))
                
                #feat.append("0="+jdict["0"])
                #feat.append("1="+jdict["1"])
                #feat.append("2="+jdict["2"])
                #feat.append("3="+jdict["3"])
                #feat.append("4="+jdict["4"])
                #feat.append("5="+jdict["5"])
                #feat.append("6="+jdict["6"])
                #feat.append("nuc="+jdict["nuc"])
                #feat.append("nuc_kind="+jdict["nuc_kind"])
                #feat.append("left_nuc="+jdict["left_nuc"])
                #feat.append("right_nuc="+jdict["right_nuc"])
                #feat.append("right_kind="+jdict["right_nuc_kind"])
                
                #feat.append("dialAct="+jdict["dialAct"])
                feat.append("phrases="+jdict["phrases"])
                #feat.append("kon_type="+jdict["kontrast type"])
                #feat.append("kon_level="+jdict["kontrast level"])
                
                #if g==0:
                    #feat.append("initial_w")
                #if g==1:
                    #feat.append("second_w")                
                if g==0:
                    feat.append("initial_w")
                elif g==1:
                    feat.append("second_w")
                else:
                    feat.append("middle")                 

                try:  # remove Y values from dict to create Y
                    accent = jdict["accents_strength"]
                    del jdict["accents_strength"]
                except:
                    accent = "0"

                X_seq.append(feat)
                #if len(X_seq)==13:
                    #print "13"
                
                # labels cannot be "0"
                if accent == "full" or accent == "weak":
                    y_seq.append("2")
               # elif accent == "weak":
                    #y_seq.append("1")
                else:
                    y_seq.append("0")

                
        X_data.append(X_seq)
        y_data.append(y_seq) 
            
    all_d = []
    for x,y in zip(X_data,y_data):
        if not x:
            continue
        else:
            assert len(x)==len(y)
            all_d.append((x,y))
    return all_d    
        
    #X = []
    #Y = []
    #for x,y in zip(X_data,y_data):
        #if not x:
            #continue
        #else:
            #assert len(x)==len(y)
            #X.append(x)
            #Y.append(y)            
    #return X, Y

def k_fold_cross_validation(data_path, k=10, randomize=False):
    """k fold cross validation of data"""
    all_d = load_data(data_path)

    if randomize:
        rnd_seed = "stay"
        shuffle(all_d)

    slices = [all_d[i::k] for i in xrange(k)]

    for i in xrange(k):
        validation = slices[i]
        
        training = [item
                    for s in slices if s is not validation
                    for item in s]
        # unpack to 4 sets
        X_test = []
        y_test = []
        for (x,y) in validation:
            X_test.append(x)
            y_test.append(y)
            
        X_train = []
        y_train = []
        for (x,y) in training:
            X_train.append(x)
            y_train.append(y)
            
        
       
        yield X_train, y_train, X_test, y_test

def data_prep():
    
    data_path = '../out_85175'
    X, y = load_datap(data_path)
    test_index = sample(range(len(X)), int(0.1*len(X)))
    X_train = []
    X_test = []
    y_train = []
    y_test = []
    for i in xrange(len(X)):
        if i in test_index:
            X_test.append(X[i])
            y_test.append(y[i])
        else:
            X_train.append(X[i])
            y_train.append(y[i])
            
    return X_train, y_train, X_test, y_test

        
        
        
        


# split to train and test
# pickle
