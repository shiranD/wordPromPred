#! /opt/local/bin/python
from __future__ import division
from os import walk
import json
import numpy as np
from random import shuffle,sample
from sklearn.feature_extraction import DictVectorizer


def suffle_data(data, bound): # shuffle folders
    new_bound  = [0]
    for bor in bound:
        new_bound.append(new_bound[-1]+bor)
    new_bound.append(len(data)-1)
    num_chuncks = len(new_bound)-1
    shuff_chunks = range(num_chuncks)
    shuffle(shuff_chunks)
    new_data = []
    for ch in shuff_chunks:
        new_data.extend(data[new_bound[ch]:new_bound[ch+1],:])
    return np.array(new_data)


def load_data(datapath):
    """load data"""

    x_data = []
    y_data = []
    d_len = []
    for (i, supdir) in enumerate(walk(datapath)):
        prefix = supdir[0] + '/'
        suffixes = supdir[2]
        if suffixes == ["config_swbd.yml"]:
            continue

        for (c,suffix) in enumerate(suffixes):
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
        
                
        d_len.append(c)
        
    vec = DictVectorizer()
    x_data = vec.fit_transform(x_data).toarray()
    data = np.zeros((len(x_data), len(x_data[0]) + 1), dtype=int)
    data[:, :-1] = x_data
    data[:, -1] = y_data
    return data,d_len

        
def chunks(items, n):
    """ Yield successive n-sized chunks from l.
    """
    for i in xrange(0, len(items), int(n/2)):
        chunk = items[i:i+n]
        yield list(set(items) - set(chunk)), chunk

        

if __name__ == '__main__':

    data_path = '../out_52947'
    all_data, bounds = load_data(data_path)
    all_data  = suffle_data(all_data, bounds) # suffle folders
    n_samples = 41620
    itms = range(n_samples)        
    x_size = len(all_data[0])-1
    flag = 1
    N = 5
    num_iter = 2
    count = 1
    
    # many utterances begin with wrong last label info   
    # two class classificaotion
    for it in xrange(num_iter):
        
        data = suffle_data(all_data, bounds) # suffle folders
        
        for idx_train, idx_test in chunks(itms, int(n_samples/10)):
               
            X_train = data[idx_train, :-1]
            Y_train = data[idx_train, -1]
            X_test = data[idx_test, :-1]
            Y_test = data[idx_test, -1]
            
            # train
            weight = np.zeros(x_size+N)
            wei_sum = np.zeros(x_size+N)
            last = np.ones(N)*(-1)
            
            for (sample, label) in zip(X_train,Y_train):
                
                sample = np.append(sample, last[-N:])                
                product = np.dot(weight,sample)
                #
                if product*label <= 0:
                    weight+= label*sample
                    wei_sum += label*sample*count
                    
                count+=1 # update count                    
    
                # hmm memory
                last = np.append(last[-N:],np.sign(product))
                
            weight -= wei_sum/count # avg weight
                            
            # test
            correct = 0
            last = np.ones(N)*(-1)
            
            for sample, label in zip(X_test,Y_test):
                
                sample = np.append(sample, last[-N:])                                
                product = np.dot(weight,sample)
                
                if np.sign(product)==label:   
                    correct+=1
                last = np.append(last[-N:],np.sign(product))
                
            print "the percision is ", correct/len(Y_test)*100
