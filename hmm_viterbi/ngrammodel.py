#! /opt/local/bin/python -O
# ngrammodel.py: n-gram smoothing and perplexity estimation
# Kyle Gorman <gormanky@ohsu.edu> and Steven Bedrick <bedricks@ohsu.edu>
#
# This script defines classes representing different conditional
# probability estimators. Conditional frequency and probability
# distributions are consistently represented as dictionaries of
# dictionaries, with the the prefix as the outer key and the suffix
# as the inner key.

from __future__ import division

from collections import defaultdict

from ngrams import ngrams
from bitweight import BitWeight, INF
import fileinput 
import re
import csv
from dataset_devision import construct_dataset, make_train


OOV_VOCABULARY_SIZE = 10000 
# imagined size of OOV vocabulary; of course it's infinite but it has to
# be set to some some finite value; this is the same default value as 
# used in OpenGRM

def create_w_po_corpus(sentences):
    f1 = open('po_w_train.txt','w')
    for sentence in sentences:  
        sp = sentence.split(' ')
        po_w = [s.split('/') for s in sp]
        return po_w       

def create_po_corpus(sentences):
    f1 = open('pos_sentence.txt','w')
    for sentence in sentences:       
        reg = re.findall('\/\w{1,30}\ ', sentence)
        temp = ''.join(reg)
        new_pos = temp.replace('/', '')
        f1.write(new_pos) 
        f1.write('\n')
    f1.close()
    po_sen = [line.rstrip() for line in open('pos_sentence.txt','r')]
    po_corpus = [line.split() for line in po_sen]    
    
    return po_corpus

class MaximumLikelihoodNGramModel(object):

    """
    n-gram model with maximum likelihood estimation
    """

    def __init__(self, corpus, order):
        self.order = order
        self._compute_prob(corpus)

    # called in constructor
    def _compute_prob(self, corpus):
        """
        Compute a conditional frquency distribution and normalize it into
        BitWeight probabilities
        """
        # conditional frequency distribution representation
        self.freq = defaultdict(lambda: defaultdict(int))
        # populate it
        for (prefix, suffix) in ngrams(corpus, self.order):
            self.freq[prefix][suffix] += 1
        # initialize log2 probability distribution with default value (0)
        self.prob = defaultdict(lambda: defaultdict(lambda: BitWeight()))
        # populate seen probabilities
        for (prefix, suffixes) in self.freq.iteritems():
            # prefix is a tuple of tokens, sffixes is a dictionary
            # containing token: count key/value pairs
            denominator = BitWeight(sum(suffixes.values()))
            # optimize dictionary lookup; both of these are pointers, so
            # modifying pdist (as we will) modifies self.prob too
            fdist = self.freq[prefix]
            pdist = self.prob[prefix]
            # normalize, using fdist[suffix], the full n-gram's count
            for suffix in suffixes:
                # BitWeight class implements division as log-space
                # subtraction so as to forestall underflow
                pdist[suffix] = BitWeight(fdist[suffix]) / denominator

    def __repr__(self):
        return '{}()'.format(self.__class__.__name__)

    def perplexity(self, corpus):
        """
        Compute per-token perplexity. The cross-entropy of p with respect
        to q is defined as: 

        H(p, q) = \sum_x p(x) log_2 q(x)

        In the case of language modeling, q is the estimated probability
        distribution and p is the (MLE) probability of each n-gram in the 
        held-out data. Then, the perplexity of p w.r.t. q is simply

        PPX(p, q) = 2^{H / Z}

        where Z is the number of tokens in p.
        """
        # frequency of observations over corpus
        fx = defaultdict(int)
        # number of observations in corpus
        Z = 0
        for (prefix, suffix) in ngrams(corpus, self.order):
            Z += 1
            fx[(prefix, suffix)] += 1
        # collect entropy
        H = BitWeight(1.)
        for ((prefix, suffix), f_x) in fx.iteritems():
            H *= f_x * self.prob[prefix][suffix]
        # divide to get per-token entropy, exponentiate to get perplexity
        return 2 ** (H.bw / Z)    
    

if __name__ == '__main__':
    data_path = '../out_52947'    
    dict_X_test, dict_y_test, dict_X_train, dict_y_train = construct_dataset(data_path)
    obs, hid_corpus, codebook = make_train(dict_X_train, dict_y_train)
    
    #transitions_ML = MaximumLikelihoodNGramModel(label_corpus,2).prob.items() # transitions 
    #transitions_WB = WittenBellNGramModel(po_corpus, order=3).wb.items() 
    #emissions_ML = MaximumLikelihoodNGramModel(obs_corpus,2).prob.items() # transitions 
    #emissions_WB = WittenBellNGramModel(w_po_corpus, order=2).wb.items()     