#! /opt/local/bin/python -O
# ngrams.py: get a stream of n-grams from a corpus
# Kyle Gorman <gormanky@ohsu.edu> and Steven Bedrick <bedricks@ohsu.edu>
# taken from NLP class at OHSU from http://www.cslu.ogi.edu/~gormanky/courses/CS662/

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

def ngrams(corpus, order):
    """
    Given a corpus (a list of "sentences", themselves lists of tokens), 
    generate n-grams of a specified order.

    Initialize a "corpus":

    >>> s1 = 'WE HOLD THESE TRUTHS TO BE SELF-EVIDENT'
    >>> s2 = 'ALL MEN ARE CREATED EQUAL' 
    >>> corpus = [s1.split(), s2.split()]

    By convention, unigrams have the empty tuple () as prefix:

    >>> next(ngrams(corpus, 1))
    ((), 'WE')

    All orders > 1 are padded. Bigrams have a single-token prefix:

    >>> the_ngrams = ngrams(corpus, 2)
    >>> next(the_ngrams)
    (('<S_0>',), 'WE')
    >>> next(the_ngrams)
    (('WE',), 'HOLD')

    Because of this paddding, no order an be "too big" for a sentence:

    >>> the_ngrams = ngrams(corpus, 6)
    >>> next(the_ngrams)
    (('<S_0>', '<S_1>', '<S_2>', '<S_3>', '<S_4>'), 'WE')
    """
    if order < 0:
        raise ValueError('Order must be integer > 0')
    left_pad = ['<S_{}>'.format(i) for i in xrange(order - 1)]
    right_pad = ['</S_{}>'.format(i) for i in xrange(order - 2, -1, -1)]
    for sentence in corpus:
        padded_sentence = left_pad + sentence + right_pad
        for i in xrange(len(padded_sentence) - order + 1):
            prefix = tuple(padded_sentence[i:i + order - 1])
            yield (prefix, padded_sentence[i + order - 1])


if __name__ == '__main__':
    import doctest
    doctest.testmod()