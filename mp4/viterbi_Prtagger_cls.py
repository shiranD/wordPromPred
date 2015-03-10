#! /opt/local/bin/python -O
# MP4 skeleton implementation
# Kyle Gorman <gormanky@ohsu.edu>

from __future__ import division


from random import Random, sample
from nltk import str2tuple
from functools import partial
from string import punctuation
from operator import itemgetter
from collections import defaultdict
from ngrammodel import MaximumLikelihoodNGramModel

# reusing this from MP3, but not the larger AveragedPerceptron class
from perceptron import LazyWeight
from dataPrep import k_fold_cross_validation
import itertools
import numpy as np


DIGIT = "*DIGIT*"

PUNCTUATION = frozenset(punctuation)
NUMBER_WORDS = frozenset("""
zero one two three four five six seven eight nine ten eleven twelve
thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty
thirty fourty fifty sixty seventy eighty ninety hundred thousand million
billion trillion quadrillion
""".upper().split())


def extract(History):

    if not History:
        return []
    if len(History) == 1:
        return History[0]
    else:
        return History[-1]


def shuffle_set(x, y):

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
    ["t_i-1='MD'", "t_i-2=','", "t_i-3='JJ'", "t_i-2=',',t_i-1='MD'",
    "t_i-3='JJ',t_i-2=',',t_i-1='MD'"]

    History is smaller than the order, but no index-out-of-bounds errors:

    >>> partial_yyhat = ["NNP"]
    >>> tfeats(partial_yyhat, 2)
    ["t_i-1='NNP'"]
    """
    if order == 0 or len(partial_yyhat) == 0:
        return []

    t_list = []
    order = min(order, len(partial_yyhat))
    for i in xrange(order):
        t_list.append("t_i-" + str(i + 1) + "='" + partial_yyhat[-i - 1] + "'")

    tt_list = t_list[::-1]

    for i in xrange(order - 1):
        combo = tt_list[-2 - i:]
        st = ""
        for st1 in combo:
            st += st1 + ","
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

    def score(self, phi, yhat):
        """
        Get scores for a particular class according to the feature vector `phi`
        """
        return sum(self.weights[phi_i][yhat].get() for phi_i in phi)

    def scores(self, phi):
        """
        Get scores for all classes according to the feature vector `phi`
        """
        scores = dict.fromkeys(self.classes, 0)
        # print scores
        for phi_i in phi:
            for (cls, weight) in self.weights[phi_i].iteritems():
                scores[cls] += weight.get()
        return scores

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
        using Viterbi returning a (list of tags, list of list of features)
        tuple; use the `tag` instance method if you want to ignore the features
        returned
        """

        # build array of dicts
        state_dicts = []
        for e_phi in efeats:
            state_dicts = self.viterbi(e_phi, state_dicts)

        # trace back
        yyhat, phis = self.traceback(efeats, state_dicts)
        assert len(efeats) == len(yyhat)

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
            # print(i)
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
        corect = 0
        incorect = 0
        for (tokens, tags) in zip(feats, tag_set):
            yyhat = self.tag(tokens)
            for pre, tag in zip(yyhat, tags):
                if pre == tag:
                    corect += 1
                else:
                    incorect += 1

        return corect / (corect + incorect)

    def viterbi(self, e_phi, states_dict):
        """compute the current states scores
        basing on the previous score, previous states
        and the current emission state score. save history of 2 past
        states and score of previous one that its 'partial score' was the
        highest. The max score is partial score and efeats score."""

        states = ["0", "1", "2"]

        if not states_dict:
            first_dict = {}
            for state in states:
                S_e = self.score(e_phi, state)
                first_dict[state] = (S_e, ([]))
            return [first_dict]

        else:
            last_dict = states_dict[-1]
            this_dict = {}
            scores = self.scores(e_phi)
            for (state, S_e) in scores.iteritems():
                S_max = -float('inf')
                for prev in states:
                    (Sprev, (Hprev)) = last_dict[prev]
                    if not Hprev:
                        Hstate = [prev]  # no history
                    else:
                        # print Hprev
                        Hstate = Hprev[-1:] + [prev]  # have two states
                        # print Hstate
                    t_phi = tfeats(Hstate, self.order)
                    partial_score = Sprev + self.score(t_phi, state)
                    if S_max < partial_score:
                        S_max = partial_score
                        max_hstate = Hstate
                # write to dict
                this_dict[state] = (S_max + S_e, (max_hstate))  # brakets
            states_dict.append(this_dict)
            return states_dict

    def traceback(self, efeats, states_dict):
        """return the tag sequence and its
        corresponding phis """

        states = ["0", "1", "2"]
        yyhat = []
        phis = []

        if len(states_dict) == 1:
            last_dict = states_dict[0]
            last_efeat = efeats[0]

        else:
            last_dict = states_dict[-1]
            last_efeat = efeats[-1]

        (state, (_, Hstate)) = max(last_dict.iteritems(), key=itemgetter(1))

        yyhat.append(state)
        phi = last_efeat + tfeats(Hstate, self.order)
        phis.append(phi)

        for (last_dict, e_phi) in zip(reversed(states_dict[:-1]),
                                      reversed(efeats[:-1])):
            prev_state = extract(Hstate)

            # if H=["2"]->["2"] need "2". H[-1:]
            (_, Hstate) = last_dict[prev_state]
            yyhat.append(prev_state)
            phi = e_phi + tfeats(Hstate, self.order)
            phis.append(phi)

        return yyhat[::-1], phis[::-1]

    def register_classes(self, claslist):
        """register classes"""

        for cls in claslist:
            self.classes.add(cls)

if __name__ == "__main__":
    path = '../out_85175'
    acc5 = []
    acc10 = []
    acc20 = []
    acc30 = []
    acc50 = []
    acc70 = []
    # the same set!
    for X_train, y_train, X_test, y_test in k_fold_cross_validation(path, 10,randomize=True): 
        
        # 5
        tagger = AveragedPerceptronTagger(order=2)
        tagger.register_classes(["0", "1", "2"])
        tagger.fit(X_train, y_train, epochs=5)
        ac = tagger.evaluate(X_test, y_test)
        acc5.append(ac)        
        # 10
        tagger = AveragedPerceptronTagger(order=2)
        tagger.register_classes(["0", "1", "2"])
        tagger.fit(X_train, y_train, epochs=10)
        ac = tagger.evaluate(X_test, y_test)
        acc10.append(ac)
        # 20
        tagger = AveragedPerceptronTagger(order=2)
        tagger.register_classes(["0", "1", "2"])
        tagger.fit(X_train, y_train, epochs=20)
        ac = tagger.evaluate(X_test, y_test)
        acc20.append(ac)
        # 30
        tagger = AveragedPerceptronTagger(order=2)
        tagger.register_classes(["0", "1", "2"])
        tagger.fit(X_train, y_train, epochs=30)
        ac = tagger.evaluate(X_test, y_test)
        acc30.append(ac)
        # 50
        tagger = AveragedPerceptronTagger(order=2)
        tagger.register_classes(["0", "1", "2"])
        tagger.fit(X_train, y_train, epochs=50)
        ac = tagger.evaluate(X_test, y_test)
        acc50.append(ac)
        # 70
        tagger = AveragedPerceptronTagger(order=2)
        tagger.register_classes(["0", "1", "2"])
        tagger.fit(X_train, y_train, epochs=70)
        ac = tagger.evaluate(X_test, y_test)
        acc70.append(ac)        
        
    print "Accuracy over 10-fold 5 epoch: {:.4f}".format(np.mean(acc5))
    print "Accuracy over 10-fold 10 epoch: {:.4f}".format(np.mean(acc10))
    print "Accuracy over 10-fold 20 epoch: {:.4f}".format(np.mean(acc20))
    print "Accuracy over 10-fold 30 epoch: {:.4f}".format(np.mean(acc30))
    print "Accuracy over 10-fold 50 epoch: {:.4f}".format(np.mean(acc50))
    print "Accuracy over 10-fold 70 epoch: {:.4f}".format(np.mean(acc70))
    
    
    
        
        
        # shuffle and have k fold
        # average on accuracy
        #X_train, y_train, X_test, y_test = data_prep()
        #trans = MaximumLikelihoodNGramModel(y_train, 3).prob.items()  # transitions    
    
    #accuracy, w = tagger.evaluate(X_test, y_test)
    #trs = ["t_i-2='0',t_i-1='0'", "t_i-2='0',t_i-1='1'", "t_i-2='0',t_i-1='2'",
           #"t_i-2='1',t_i-1='0'", "t_i-2='1',t_i-1='1'", "t_i-2='1',t_i-1='2'",
          # "t_i-2='2',t_i-1='0'", "t_i-2='2',t_i-1='1'", "t_i-2='2',t_i-1='2'"]
    #for tr in trs:
        #print tr
        #print w[tr]
    #print "Accuracy: {:.4f}".format(accuracy)
