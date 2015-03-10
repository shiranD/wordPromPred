#! /opt/local/bin/python

from os import walk
import json
import numpy as np
from random import shuffle
from sklearn.feature_extraction import DictVectorizer
from sklearn.svm import SVC
from sklearn import linear_model


def load_data(datapath):
    """load data"""
    
    x_data = []
    y_data = []
    
    for (i,supdir) in enumerate(walk(datapath)):
        prefix = supdir[0] + '/'        
        suffixes = supdir[2]
        if suffixes == ["config_swbd.yml"]:
            continue
        
        for suffix in suffixes:
            jfilename = prefix + suffix
            with open(jfilename) as fjson:
                # read json as dict
                jdict = json.load(fjson)
                try: # remove Y values from dict to create Y
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
    data = np.zeros((len(x_data),len(x_data[0])+1),dtype=int)
    data[:,:-1] = x_data
    data[:,-1] = y_data
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
    #items = range(len(all_data))
    items = range(5000)
    rbf = []
    linear_svm = []
    poly = []
    sigmoid = []
    lin_reg = []
    sgd = []
    for idx_train, idx_test in k_fold_cross_validation(items, 5):
        
        X_train = all_data[idx_train,:-1]
        Y_train = all_data[idx_train,-1]        
        X_test = all_data[idx_test,:-1]
        Y_test = all_data[idx_test,-1]
        if 0: # svm rbf kernel
            clf = SVC()
            clf.fit(X_train, Y_train)
            Y_predict = clf.predict(X_test)
            print "rbf",np.mean(Y_predict == Y_test) 
            rbf.append(np.mean(Y_predict == Y_test))
            
        if 0: # svm linear kernel
            clf = SVC(C=1.0, kernel='linear')
            clf.fit(X_train, Y_train)
            Y_predict = clf.predict(X_test)
            print "linear svm", np.mean(Y_predict == Y_test) 
            linear_svm.append(np.mean(Y_predict == Y_test)) 
            
        if 0: # svm poly kernel
            clf = SVC(C=1.0, kernel='poly')
            clf.fit(X_train, Y_train)
            Y_predict = clf.predict(X_test)
            print "poly svm", np.mean(Y_predict == Y_test) 
            poly.append(np.mean(Y_predict == Y_test))  
            
        if 0: # svm sigmoid kernel    
            clf = SVC(C=1, kernel='sigmoid')
            clf.fit(X_train, Y_train)
            Y_predict = clf.predict(X_test)
            print "sigmoid svm", np.mean(Y_predict == Y_test) 
            sigmoid.append(np.mean(Y_predict == Y_test)) 
        
        if 1: # linear sgd with svm
            clf = linear_model.SGDClassifier(loss='perceptron',alpha=0.001)
            clf.fit(X_train, Y_train)
            Y_predict = clf.predict(X_test)
            print "sgd svm", np.mean(Y_predict == Y_test) 
            sgd.append(np.mean(Y_predict == Y_test))      
            
    #print "avg accuracy of rbf is ", np.mean(rbf) 
    #print "avg accuracy of linear_svm is ", np.mean(linear_svm) 
    #print "avg accuracy of poly is ", np.mean(poly) 
    #print "avg accuracy of sigmoid is ", np.mean(sigmoid) 
    print "avg accuracy of sgd is ", np.mean(sgd) 
    
        
        #for item in items:
            #assert (item in idx_train) ^ (item in idx_test)


        
        