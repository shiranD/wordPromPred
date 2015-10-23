#! /opt/local/bin/python -O
# MP3 skeleton implementation
# Kyle Gorman <gormanky@ohsu.edu>
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

from __future__ import division

from random import Random
from functools import partial
from collections import defaultdict


class LazyWeight(object):

    """
    Helper class for `MulticlassAveragedPerceptron`:

    Instances of this class are essentially triplets of values which
    represent a weight of a single feature in an averaged perceptron.
    This representation permits "averaging" to be done implicitly, and
    allows us to take advantage of sparsity in the feature space.
    First, as the name suggests, the `summed_weight` variable is lazily
    evaluated (i.e., computed only when needed). This summed weight is the
    one used in actual inference: we need not average explicitly. Lazy
    evaluation requires us to store two other numbers. First, we store the
    current weight, and the last time this weight was updated. When we
    need the real value of the summed weight (for inference), we "freshen"
    the summed weight by adding to it the product of the real weight and
    the time elapsed.

    # initialize
    >>> t = 0
    >>> lw = LazyWeight(t=t)
    >>> t += 1
    >>> lw.update(t, 1)
    >>> t += 1
    >>> lw.get()
    1

    # some time passes...
    >>> t += 1
    >>> lw.get()
    1

    # weight is now changed
    >>> lw.update(-1, t)
    >>> t += 3
    >>> lw.update(-1, t)
    >>> t += 3
    >>> lw.get()
    -1
    """

    def __init__(self, default_factory=int, t=0):
        self.timestamp = t
        self.weight = default_factory()
        self.summed_weight = default_factory()

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self.__dict__)

    def get(self):
        """
        Return current weight
        """
        return self.weight

    def _freshen(self, t):
        """
        Apply queued updates, and update the timestamp
        """
        self.summed_weight += (t - self.timestamp) * self.weight
        self.timestamp = t

    def update(self, value, t):
        """
        Bring sum of weights up to date, then add `value` to the weight
        """
        self._freshen(t)
        self.weight += value

    def average(self, t):
        """
        Set `self.weight` to the summed value, for final inference
        """
        self._freshen(t)
        self.weight = self.summed_weight / t


class MulticlassAveragedPerceptron(object):
    """
    Multiclass classification via the averaged perceptron. Features
    are assumed to be binary, hashable (e.g., strings), and very sparse. 
    Labels must also be hashable.
    """

    def __init__(self, default=None, seed=None):
        self.classes = {default}
        self.random = Random(seed)
        self.weights = defaultdict(partial(defaultdict, LazyWeight))
        self.time = 0
    
    def fit(self, Y, Phi, epochs, alpha=1):
        # copy data so we can mutate it in place
        data = list(zip(Y, Phi))
        for _ in xrange(epochs):
            self.random.shuffle(data)
            for (y, phi) in data:
                self.fit_one(y, phi)
        self.finalize()

    def fit_one(self, y, phi, alpha=1):
        self.classes.add(y)
        yhat = self.predict(phi)
        if y != yhat:
            self.update(y, yhat, phi, alpha)

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

    def predict(self, phi):
        """
        Predict the most likely class for `phi`
        """
        scores = dict.fromkeys(self.classes, 0)
        for phi_i in phi:
            for (cls, weight) in self.weights[phi_i].iteritems():
                scores[cls] += weight.get()
        (yhat, _) = max(scores.iteritems(), key=itemgetter(1))
        return yhat

    def finalize(self):
        """
        Prepare for inference by applying averaging

        TODO(kbg): also remove zero-valued weights?
        """
        for (phi_i, clsweights) in self.weights.iteritems():
            for (cls, weight) in clsweights.iteritems():
                weight.average(self.time)
