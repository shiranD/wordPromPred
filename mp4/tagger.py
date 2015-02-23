#! /opt/local/bin/python -O
# MP4 skeleton implementation
# Kyle Gorman <gormanky@ohsu.edu>

from __future__ import division


from random import Random
from nltk import str2tuple
from functools import partial
from string import punctuation
from operator import itemgetter
from collections import defaultdict

# reusing this from MP3, but not the larger AveragedPerceptron class
from perceptron import LazyWeight


DIGIT = "*DIGIT*"

PUNCTUATION = frozenset(punctuation)
NUMBER_WORDS = frozenset("""
zero one two three four five six seven eight nine ten eleven twelve 
thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty 
thirty fourty fifty sixty seventy eighty ninety hundred thousand million 
billion trillion quadrillion
""".upper().split())


# helper for reading things in


def tagged_corpus(filename):
    """
    Lazily read tagged corpus from a file `filename`
    """
    try:
        with open(filename, "r") as source:
            for line in source:
                (tokens, tags) = zip(*(str2tuple(wt) for wt in
                                       line.split()))
                yield (list(tokens), list(tags))
    except IOError as error:
        exit(error)


def efeats(tokens):
    """
    For each token in the utterance, extract a list of emission feature 
    strings. Before extract, any token consisting solely of digits is
    mapped to a special token `*DIGIT*`. Then, for each token, we extract 
    the following features:

    * bias
    * orthographic features:
        - first character of the current token (case-insensitive)
        - three-character suffix of the preceding token (case-insensitive)
        - three-character suffix of the current token (case-insensitive)
        - token is purely alphabetic?
        - token is "numberlike", defined by being one of:
            * a digit string (`*DIGIT*`)
            * a string of digits with one intervening `/` (e.g., `3/4`)
            * a string of digits with one or more intervening '.'s or 
              ','s (e.g., `9.99`, `1,000`)
            * an alphabetic number word (e.g., `fourty`)
        - token is all caps
        - token is all lowercase
        - token is in "titlecase" (e.g., `President`)
        - token is purely punctuation (use `string.punctuation`)
        - token contains a hyphen
    * context features (all case-insensitive):
        - two tokens back
        - previous token
        - current token
        - the next token
        - two tokens back

    For instance, for the sequence ["See", "Spot", "run", "."], you might 
    produce something like:

    [["*bias*", "pre1(w_i)='S'", "suf3(w_i)='SEE', "suf3(w_i+1)='SPO', 
      "*alphabetic*", "*titlecase*', "*initial*", "w_i='SEE', 
      "w_i+1='SPOT', "w_i+2='RUN"],
     ["*bias*", "pre1(w_i)='S'", "suf3(w_i-1)='SEE', "suf3(w_i)='SPO'"
       "suf3(w_i+1)='RUN'", "*alphabetic*", "*lowercase*", 
       "*second-token*", "w_i-1='SEE'", "w_i='SPOT'", "w_i+1='RUN'",
       "w_i+2='.'"],
       # and so on...
    ]

    However, you are permitted to encode the features however (and in 
    what order) you wish, so long as you avoid redundant computations.

    NB: this returns a list of lists (because it is for a whole sentence),
    not a list like `tfeats` does.
    """
    e_list = []
    for i, token in enumerate(tokens):
        l_token = []
        l_token.append("*bias*")
        # first i
        l_token.append("pre1(w_i)="+token[0].upper())
        # suf i
        idx = min(3,len(token))
        l_token.append("suf3(w_i)="+token[-idx:].upper())  
        
        if i!=len(tokens)-1:
            # suf i+1        
            idx = min(3,len(tokens[i+1]))
            l_token.append("suf3(w_i+1)="+tokens[i+1][-idx:].upper())            
        
        boo = all(e.isalpha() for e in token)          
        if boo: 
            l_token.append("*alphabetic*")
            boo2 = all(e.upper() for e in token)
            if boo2: # letter case
                l_token.append("*uppercase*")
            else:
                boo3 = all(e.lower() for e in token)
                if boo3:
                    l_token.append("*lowercase*")
                else:
                    l_token.append("*titlecase*")
        else:
            # digit
            dig = any(e.isdigit() for e in token)
            if token in NUMBER_WORDS or dig:
                l_token.append("*numberlike*")
            else:
                # punctuation
                punc = all(e in punctuation for e in token)
                if punc:
                    l_token.append("*punctuation*")
                    
        
        if i > 1:            
            l_token.append("2prev="+tokens[i-1].upper()+" "+tokens[i-2].upper())
        if i > 0:
            l_token.append("prev="+tokens[i-1].upper())

        l_token.append("curr="+token.upper())
        try:
            a = tokens[i+1]
            l_token.append("fut="+tokens[i+1].upper())  
        except:
            pass
        try:
            a = tokens[i+2]
            l_token.append("2fut="+tokens[i+1].upper()+" "+tokens[i+2].upper())
        except:
            pass
            

        e_list.append(l_token)
        
    #if len(tokens)==2 or len(tokens)==1:
        #print e_list    
        
    return e_list
    
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
    if order==0 or len(partial_yyhat)==0 or partial_yyhat==[None]:
        return []

    t_list = []
    order = min(order, len(partial_yyhat))
    for i in xrange(order):
        t_list.append("t_i-"+str(i+1)+"='"+partial_yyhat[-i-1]+"'")
        
    tt_list = t_list[::-1]
            
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

    def tag_with_features(self, tokens):
        """
        Tag a list of tokens using a greedy approximation of an HMM,
        returning a (list of tags, list of list of features) tuple; use
        the `tag` instance method if you want to ignore the features 
        returned
        """
        yyhat = []
        phis = []
        for e_phi in efeats(tokens):
            phi = e_phi + tfeats(yyhat, self.order)
            yhat = self.predict(phi)
            yyhat.append(yhat)
            phis.append(phi)
        return (yyhat, phis)

    def tag(self, tokens):
        """
        Tag a list of tokens using a greedy approximation of an HMM
        """
        (yyhat, _) = self.tag_with_features(tokens)
        return yyhat

    def fit(self, tagged_corpus, epochs, alpha=1):
        """
        Fit the tagger model 
        """
        # make an (evaluated) copy of the data, to shuffle it in place
        my_tagged_corpus = list(tagged_corpus)
        for i in xrange(1, 1 + epochs):
            #print(i)
            self.random.shuffle(my_tagged_corpus)
            for (tokens, tags) in my_tagged_corpus:
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

    def evaluate(self, tagged_corpus):
        """
        Tag held-out labeled corpus `tagged_corpus`, and return tagging
        accuracy
        """
        my_tagged_corpus = list(tagged_corpus)
        corect=0
        incorect=0        
        for (tokens, tags) in my_tagged_corpus:
            yyhat= self.tag(tokens)
            for pre, tag in zip(yyhat,tags):
                if pre==tag:
                    corect+=1
                else:
                    incorect+=1

        return corect/(corect+incorect)
                

if __name__ == "__main__":
    tagger = AveragedPerceptronTagger(order=2)
    #tagger.fit(tagged_corpus("trn_00-18.pos"), epochs=20)
    accuracy = tagger.evaluate(tagged_corpus("dev_19-21.pos"))
    print "Accuracy: {:.4f}".format(accuracy)
