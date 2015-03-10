#! /opt/local/bin/python

from os import walk
import json
import numpy as np
from random import shuffle,sample
from sklearn.feature_extraction import DictVectorizer
from sklearn.svm import SVC
from sklearn import linear_model


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
                if 1:
                    del jdict["tag"]
                if 1:
                    del jdict["collps_tag"]
                if 1:
                    del jdict["function"]
                if 1:
                    del jdict["negation"]
                if 1:
                    del jdict["0"]
                    del jdict["1"]                   
                    del jdict["2"]
                    del jdict["3"]
                    del jdict["4"]
                    del jdict["5"]
                    del jdict["6"]
                if 1:
                    del jdict["nuc"]
                    del jdict["nuc_kind"]
                if 1:
                    del jdict["dialAct"]
                if 1:
                    del jdict["left_nuc"]
                    try:
                        del jdict["left_nuc_kind"]
                    except:
                        pass
                    del jdict["right_nuc"]
                    del jdict["right_nuc_kind"]
                if 1:
                    del jdict["phrases"]
                if 1:
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
                    y_data.append(2)
                else:
                    y_data.append(0)

                x_data.append(jdict)
                x_data

    vec = DictVectorizer()
    x_data = vec.fit_transform(x_data).toarray()
    data = np.zeros((len(x_data), len(x_data[0]) + 1), dtype=int)
    data[:, :-1] = x_data
    data[:, -1] = y_data
    return data


def k_fold_cross_validation(items, k, randomize=False):
    """k fold cross validation of data"""

    if randomize:
        items = list(items)
        shuffle(items)

    slices = [items[i::k] for i in xrange(k)]

    for i in xrange(k):
        validation = slices[i]
        training = [item
                    for s in slices if s is not validation
                    for item in s]
        yield training, validation


if __name__ == '__main__':

    data_path = '../out_52947'
    all_data = load_data(data_path)
    #itms = range(len(all_data))
    n_samples = 10000
    #n_samples = 10
    
    idx = sample(range(len(all_data)),n_samples)
    itms = range(n_samples)        
    all_data = all_data[idx]
    rbf = []
    linear_svm = []
    poly = []
    sigmoid = []
    lin_reg = []
    sgd = []
    BL = []
    null = []
    weak = []
    full = []
    for idx_train, idx_test in k_fold_cross_validation(itms, 5,randomize=True):

        X_train = all_data[idx_train, :-1]
        Y_train = all_data[idx_train, -1]
        X_test = all_data[idx_test, :-1]
        Y_test = all_data[idx_test, -1]
        #BL.append(np.mean(Y_test==0))
        #print "BL is ",np.mean(Y_test==0)

        if 1:  # svm linear kernel
            clf = SVC(C=1.0, kernel='linear')
            clf.fit(X_train, Y_train)
            acc = clf.score(X_test, Y_test)
            #print "linear svm", acc
            linear_svm.append(acc)
            
            Y_predict = clf.predict(X_test)
            idx = np.where(Y_predict == Y_test)[0]
            if np.where(Y_test[idx]==0)[0].any():
                null.append(len(np.where(Y_test[idx]==0)[0]))
            if np.where(Y_test[idx]==2)[0].any():
                weak.append(len(np.where(Y_test[idx]==2)[0]))
            if np.where(Y_test[idx]==1)[0].any():
                full.append(len(np.where(Y_test[idx]==1)[0]))
            
            
    for idx_train, idx_test in k_fold_cross_validation(itms, 5, randomize=True):

        X_train = all_data[idx_train, :-1]
        Y_train = all_data[idx_train, -1]
        X_test = all_data[idx_test, :-1]
        Y_test = all_data[idx_test, -1]
        #BL.append(np.mean(Y_test==0))
        #print "BL is ",np.mean(Y_test==0)  
        #get index of incorrect count how many weak full null

        if 1:  # svm linear kernel
            clf = SVC(C=1.0, kernel='linear')
            clf.fit(X_train, Y_train)
            acc = clf.score(X_test, Y_test)
            #print "linear svm", acc
            linear_svm.append(acc)    
            
            Y_predict = clf.predict(X_test)
            idx = np.where(Y_predict == Y_test)[0]
            if np.where(Y_test[idx]==0)[0].any():
                null.append(len(np.where(Y_test[idx]==0)[0]))
            if np.where(Y_test[idx]==2)[0].any():
                weak.append(len(np.where(Y_test[idx]==2)[0]))
            if np.where(Y_test[idx]==1)[0].any():
                full.append(len(np.where(Y_test[idx]==1)[0]))
            
            

    print "avg accuracy of linear_svm is ", np.mean(linear_svm),np.mean(linear_svm)*20000
    print "NN null",sum(null)
    print "YY full",sum(full)+sum(weak)
    #print "missed weak",np.mean(no_weak)
    
    #print "avg Baseline is ", np.mean(BL)
    #print "avg accuracy of linear_svm is ", np.var(linear_svm)
    
    #avg accuracy of linear_svm is  0.7731 15462.0 (all)
    #NN null 12472
    #YY full 2990    
    #TBD
    
    #ph+word+syll+kon+clp_tg
    #avg accuracy of linear_svm is  0.77735 15547.0
    #NN null 12279
    #YY full 3268    
    
    #phrase+words
    #avg accuracy of linear_svm is  0.78105 15621.0
    #NN null 12446
    #YY full 3175    
    
    #words+clp-tg
    #avg accuracy of linear_svm is  0.7286 14572.0
    #NN null 12376
    #YY full 2196    
    
    #words
    #avg accuracy of linear_svm is  0.732 14640.0
    #NN null 12088
    #YY full 2552  