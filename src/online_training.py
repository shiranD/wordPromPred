#! /opt/local/bin/python
from __future__ import division
from os import walk
import json
import numpy as np
from random import shuffle,sample
from sklearn.feature_extraction import DictVectorizer



def load_data(datapath):
    """load data"""

    x_data = []
    y_data = []

    for (i, supdir) in enumerate(walk(datapath)):
        prefix = supdir[0] + '/'
        suffixes = supdir[2]
        if suffixes == ["config_swbd.yml"]:
            continue

        for suffix in suffixes:
            jfilename = prefix + suffix
            with open(jfilename) as fjson:
                # read json as dict
                jdict = json.load(fjson)
                if 0:
                    del jdict["word"]
                if 0:
                    del jdict["tag"]
                if 0:
                    del jdict["collps_tag"]
                if 0:
                    del jdict["function"]
                if 0:
                    del jdict["negation"]
                if 0:
                    del jdict["0"]
                    del jdict["1"]                   
                    del jdict["2"]
                    del jdict["3"]
                    del jdict["4"]
                    del jdict["5"]
                    del jdict["6"]
                if 0:
                    del jdict["nuc"]
                    del jdict["nuc_kind"]
                if 0:
                    del jdict["dialAct"]
                if 0:
                    del jdict["left_nuc"]
                    try:
                        del jdict["left_nuc_kind"]
                    except:
                        pass
                    del jdict["right_nuc"]
                    del jdict["right_nuc_kind"]
                if 0:
                    del jdict["phrases"]
                if 0:
                    del jdict["kontrast type"]
                    del jdict["kontrast level"]
                                    
                
                try:  # remove Y values from dict to create Y
                    accent = jdict["accents_strength"]
                    del jdict["accents_strength"]
                except:
                    accent = 0

                if accent == "full":
                    y_data.append(1)
                elif accent == "weak":
                    y_data.append(1)
                else:
                    y_data.append(-1)

                x_data.append(jdict)
                x_data

    vec = DictVectorizer()
    x_data = vec.fit_transform(x_data).toarray()
    data = np.zeros((len(x_data), len(x_data[0]) + 1), dtype=int)
    data[:, :-1] = x_data
    data[:, -1] = y_data
    return data

        
def chunks(items, n):
    """ Yield successive n-sized chunks from l.
    """
    for i in xrange(0, len(items), int(n/2)):
        chunk = items[i:i+n]
        yield list(set(items) - set(chunk)), chunk

        

if __name__ == '__main__':

    data_path = '../out_52947'
    all_data = load_data(data_path)
    #itms = range(len(all_data))
    n_samples = 41620
    idx = sample(range(len(all_data)),n_samples)
    itms = range(n_samples)        
    all_data = all_data[idx]

    x_size = len(all_data[0])
    weight = np.zeros(x_size)
    flag = 1
    
    # many utterances begin with wrong last label info   
    # two class classificaotion
    for idx_train, idx_test in chunks(itms, int(n_samples/5)):
           
        X_train = all_data[idx_train, :-1]
        Y_train = all_data[idx_train, -1]
        X_test = all_data[idx_test, :-1]
        Y_test = all_data[idx_test, -1]
        
        # train
        weight = np.zeros(x_size)
        delta = np.zeros(x_size)
        
        for sample, label in zip(X_train,Y_train):
            
            if flag:# make a probable label for first sample
                sample = np.append(sample,[-1])
                flag = 0
            else:# predict with last label
                sample = np.append(sample,[last_label])
                
            product = np.dot(weight,sample)
            #
            if product*label <= 0:
                weight+= 0.01*label*sample

            # hmm memory
            last_label = np.sign(product)
            
        # test
        correct = 0
        for sample, label in zip(X_test,Y_test):
            
            if not flag:
                sample = np.append(sample,[-1])
                flag = 1
            else:
                sample = np.append(sample,[last_label])
                
            product = np.dot(weight,sample)
            
            if np.sign(product)==label:   
                correct+=1
            last_label = np.sign(product)
            
        print "the percision is ", correct/len(Y_test)*100
