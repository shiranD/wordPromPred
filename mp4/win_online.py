#! /opt/local/bin/python
from __future__ import division
from os import walk
import json
import numpy as np
from random import shuffle, sample
from sklearn.feature_extraction import DictVectorizer


def suffle_data(data, bound):  # shuffle folders

    num_chuncks = len(bound) - 1
    shuff_chunks = range(num_chuncks)
    shuffle(shuff_chunks)
    new_data = []
    for ch in shuff_chunks:
        new_data.extend(data[int(bound[ch]):int(bound[ch + 1]), :])
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

        for (c, suffix) in enumerate(suffixes):
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
                # labels cannot be '0'
                if accent == "full":
                    y_data.append(1)
                elif accent == "weak":
                    y_data.append(2)
                else:
                    y_data.append(3)

                x_data.append(jdict)

        d_len.append(c)

    vec = DictVectorizer()
    x_data = vec.fit_transform(x_data).toarray()
    data = np.zeros((len(x_data), len(x_data[0]) + 2), dtype=int)
    data[:, 0] = np.ones(len(x_data))
    data[:, 1:-1] = x_data
    data[:, -1] = y_data
    

    bound = [0]  # compute bounds
    for bor in d_len:
        bound.append(bound[-1] + bor)
    bound.append(len(data) - 1)

    return data, bound


def chunks(items, n):
    """ Yield successive n-sized chunks from l.
    """
    for i in xrange(0, len(items), int(n / 2)):
        chunk = items[i:i + n]
        yield list(set(items) - set(chunk)), chunk
