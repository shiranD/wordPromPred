#! /opt/local/bin/python -O
# MP4 skeleton implementation
# Kyle Gorman <gormanky@ohsu.edu>
# taken from NLP class at OHSU from http://www.cslu.ogi.edu/~gormanky/courses/CS662/
# this code was modifed by Shiran Dudy <dudy@ohsu.edu>

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

from random import Random, sample
from nltk import str2tuple
from functools import partial
from string import punctuation
from operator import itemgetter
from collections import defaultdict

# reusing this from MP3, but not the larger AveragedPerceptron class
from perceptron import LazyWeight
from dataPrep import k_fold_cross_validation
import numpy as np
from sklearn import metrics
from ac import accent_ratio, add_to_xes, add_to_xes2


DIGIT = "*DIGIT*"

PUNCTUATION = frozenset(punctuation)
NUMBER_WORDS = frozenset("""
zero one two three four five six seven eight nine ten eleven twelve 
thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty 
thirty fourty fifty sixty seventy eighty ninety hundred thousand million 
billion trillion quadrillion
""".upper().split())


# helper for reading things in

def shuffle_set(x,y):
    
    index = sample(range(len(x)), len(x))
    y_new = []
    x_new = []
    for i in xrange(len(x)):
        y_new.append(y[index[i]])
        x_new.append(x[index[i]]) 
        
    return x_new, y_new
    
    
    
def tfeats(partial_yyhat, order):
    """
    Given a list of hypothesized preceding labels `partial_yyhat` and 
    a Markov `order`, generate the transition features for the next 
    element in the sequence. The `order` parameter determines how far
    back the features may reach. Let the _history_ be the `order` 
    preceding tags in `partial_yyhat`, truncated when the `order` is 
    larger than `partial_yyhat` (i.e., near the left edge). There are two 
    types of transition tags extracted from the history:

    * a "unigram" tag for each tag in the history
    * all suffixes of the history (including the improper suffix that
      is the whole history)

    Tests with a big history:

    >>> partial_yyhat = ["NNP", "NNP", ",", "CD", "NNS", "JJ", ",", "MD"]
    >>> tfeats(partial_yyhat, 0)
    []
    >>> tfeats(partial_yyhat, 1)
    ["t_i-1='MD'"]
    >>> tfeats(partial_yyhat, 2)
    ["t_i-1='MD'", "t_i-2=','", "t_i-2=',',t_i-1='MD'"]
    >>> tfeats(partial_yyhat, 3)
    ["t_i-1='MD'", "t_i-2=','", "t_i-3='JJ'", "t_i-2=',',t_i-1='MD'", "t_i-3='JJ',t_i-2=',',t_i-1='MD'"]

    History is smaller than the order, but no index-out-of-bounds errors:

    >>> partial_yyhat = ["NNP"]
    >>> tfeats(partial_yyhat, 2)
    ["t_i-1='NNP'"]
    """
    if order==0 or len(partial_yyhat)==0:
        return []

    t_list = []
    order = min(order, len(partial_yyhat))
    for i in xrange(order):
        t_list.append("t_i-"+str(i+1)+"='"+partial_yyhat[-i-1]+"'")
        
    tt_list = t_list[::-1]# reverse
            
    for i in xrange(order-1):
        combo = tt_list[-2-i:]
        st = ""
        for st1 in combo:
            st+=st1+","
        t_list.append(st[:-1])
        
    return t_list

class AveragedPerceptronTagger(object):

    def __init__(self, order, default=None, seed=None):
        self.order = order
        self.classes = {default}
        self.random = Random(seed)
        self.weights = defaultdict(partial(defaultdict, LazyWeight))
        self.time = 0

    # low-level perceptron operations

    def scores(self, phi):
        """
        Get scores for all classes according to the feature vector `phi`
        """
        scores = dict.fromkeys(self.classes, 0)
        for phi_i in phi:
            for (cls, weight) in self.weights[phi_i].iteritems():
                scores[cls] += weight.get()
        return scores

    def predict(self, phi):
        """
        Predict most likely class for the feature vector `phi`
        """
        scores = self.scores(phi)
        (yhat, _) = max(scores.iteritems(), key=itemgetter(1))
        return yhat

    def update(self, y, yhat, phi, alpha=1):
        """
        Given feature vector `phi`, reward correct observation `y` and
        punish incorrect hypothesis `yhat`, assuming that `y != yhat`.
        `alpha` is the learning rate (usually 1).
        """
        for phi_i in phi:
            ptr = self.weights[phi_i]
            ptr[y].update(+alpha, self.time)
            ptr[yhat].update(-alpha, self.time)
        self.time += 1

    def finalize(self):
        """
        Prepare for inference by applying averaging

        TODO(kbg): also remove zero-valued weights?
        """
        for (phi_i, clsweights) in self.weights.iteritems():
            for (cls, weight) in clsweights.iteritems():
                weight.average(self.time)

    # stuff to do with tagging specifically

    def tag_with_features(self, efeats):
        """
        Tag a list of tokens using a greedy approximation of an HMM,
        returning a (list of tags, list of list of features) tuple; use
        the `tag` instance method if you want to ignore the features 
        returned
        """
        yyhat = []
        phis = []
        for e_phi in efeats:
            phi = e_phi
            yhat = self.predict(phi)
            yyhat.append(yhat)
            phis.append(phi)
            last_e_phi = e_phi
        return (yyhat, phis)

    def tag(self, tokens):
        """
        Tag a list of tokens using a greedy approximation of an HMM
        """
        (yyhat, _) = self.tag_with_features(tokens)
        return yyhat

    def fit(self, feats, tag_set, epochs, alpha=1):
        """
        Fit the tagger model 
        """
        # make an (evaluated) copy of the data, to shuffle it in place
        for i in xrange(1, 1 + epochs):
            #print(i)
            feats, tag_set = shuffle_set(feats, tag_set)            
            for (tokens, tags) in zip(feats, tag_set):
                self.fit_one(tokens, tags)
        self.finalize()

    def fit_one(self, tokens, tags, alpha=1):
        self.classes.update(tags)
        # tag sequence
        (yyhat, phis) = self.tag_with_features(tokens)
        # rescore it
        for (y, yhat, phi) in zip(tags, yyhat, phis):
            if y != yhat:
                self.update(y, yhat, phi, alpha)

    def evaluate(self, feats, tag_set):
        """
        Tag held-out labeled corpus `tagged_corpus`, and return tagging
        accuracy
        """
        corect=0
        incorect=0   
        all_pre = []
        all_tru = []
        per_sen = 0
        for (tokens, tags) in zip(feats, tag_set):
            yyhat= self.tag(tokens)     
            all_pre.extend(yyhat)
            all_tru.extend(tags)
            cor_sen = 0
            for pre, tag in zip(yyhat, tags):
                if pre==tag:
                    corect+=1
                    cor_sen+=1
                else:
                    incorect+=1
            if cor_sen == len(yyhat):
                per_sen+=1
                
        print metrics.recall_score(all_pre, all_tru, average=None)
                
        return corect/(corect+incorect), per_sen/len(tag_set) #nul/corect, ful/corect
                
    def register_classes(self, claslist):
        """register classes"""

        for cls in claslist:
            self.classes.add(cls)
            
if __name__ == "__main__":
    
    path = '../out_85175'
    acc40 = []
    rate = []    

    # the same set!
    for X_train, y_train, X_test, y_test in k_fold_cross_validation(path, 10,randomize=True): 
        print len(y_train)
        continue
        # 40
        # find accent ratio
        ar_dict = accent_ratio(X_train, y_train)
        X_train, X_test = add_to_xes(X_train, X_test, ar_dict)
        # add IC feature
        icPath = "../icJson"
        X_train, X_test = add_to_xes2(X_train, X_test, icPath)        
        
        
        tagger = AveragedPerceptronTagger(order=1)
        tagger.register_classes(["0", "2"])        
        tagger.fit(X_train, y_train, epochs=40)
        ac, sen_rate = tagger.evaluate(X_test, y_test)
        acc40.append(ac) 
        rate.append(sen_rate)
        
    print "order 1"
    #print "Accuracy over 10-fold 40 epoch: {:.4f}".format(np.mean(acc40))
    #print "Succesful sentence rate 10-fold 40 epoch: {:.4f}".format(np.mean(rate)) 
