from __future__ import division
from collections import defaultdict
from dataset_devision import construct_dataset, concat_set, shuffle_set 
import numpy as np
import random


def make_last(hmm_order, feat_size):

    pre_samples = []
    feat = np.zeros(feat_size, dtype=int)
    label = np.zeros(3, dtype=int)
    label[2] = 1  # common_class_label = 3
    for i in xrange(hmm_order):
        pre_samples.extend(feat)
        pre_samples.extend(label)

    return pre_samples

def score_all(weights, sample):

    res = np.dot(weights, sample)
    idx = np.argmax(res)
    max_value = res[idx]
    idx_2 = np.zeros(3)
    idx_2[idx] = 1
    return max_value, idx, idx_2

data_path = '../out_52947'
dict_X_test, dict_y_test, dict_X_train, dict_y_train = construct_dataset(data_path)

num_iter = 20
count = 1
N = 2
num_clas = 3
l_label = 3
# local will take only feats
l_X = len(dict_X_test[0][0])
weight = np.zeros(
    (num_clas, (l_X + l_label) * (N + 1) - l_label + (l_X) * N), dtype=float)
weight_sum = np.zeros(
    (num_clas, (l_X + l_label) * (N + 1) - l_label + (l_X) * N), dtype=float)

for it in xrange(num_iter):

    X_train, Y_train = shuffle_set(dict_X_train, dict_y_train)
    len_t = len(Y_train)

    # TRAIN
    last = make_last(N, l_X)
    for g, (sample, label) in enumerate(zip(X_train, Y_train)):
        
        # extract future sample
        if g + 1 + N > len_t:
            gap = g + 1 + N - len_t
            in_old = len_t - (g + 1)
            a = X_train[g + 1:len_t]
            b = X_train[0:gap]
            a = a.reshape((1, l_X * in_old))
            b = b.reshape((1, l_X * gap))
            fut = np.append(a, b)
        else:
            fut = X_train[g + 1:g + 1 + N, :]  # flat
            fut = fut.reshape((1, l_X * N))

        fut_sample = np.append(sample, fut)
        APsample = np.append(last[-(l_X + l_label) * N:], fut_sample)
        product, p_idx, b_idx = score_all(weight, APsample)

        if p_idx != label - 1:

            weight[label - 1] += (label - 1 - p_idx) * APsample
            weight[p_idx] -= (label - 1 - p_idx) * APsample  # true value

        # hmm memory
        greed = np.append(sample, b_idx)
        last = np.append(last[-(l_X + l_label) * N:], greed)  # update last
        count += 1  # update count
        #average and incourage
        weight_sum += (weight - weight_sum) / count

weight_sum[0]=weight_sum[0]/np.sum(weight_sum[0]) # predicted more than one class 0,1
weight_sum[1]=weight_sum[1]/np.sum(weight_sum[1])
weight_sum[2]=weight_sum[2]/np.sum(weight_sum[2])

# TEST
X_test, Y_test = concat_set(dict_X_test, dict_y_test)
correct = 0
last = make_last(N, l_X)
len_t = len(Y_test)


for g, (sample, label) in enumerate(zip(X_test, Y_test)):

    if g + 1 + N > len_t:
        gap = g + 1 + N - len_t
        in_old = len_t - (g + 1)
        a = X_train[g + 1:len_t]
        b = X_train[0:gap]
        a = a.reshape((1, l_X * in_old))
        b = b.reshape((1, l_X * gap))
        fut = np.append(a, b)
    else:
        fut = X_train[g + 1:g + 1 + N, :]  # flat
        fut = fut.reshape((1, l_X * N))

    fut_sample = np.append(sample, fut)
    APsample = np.append(last[-(l_X + l_label) * N:], fut_sample)
    product, p_idx, b_idx = score_all(weight_sum, APsample)

    if p_idx == label - 1:
        correct += 1
        print p_idx
    greed = np.append(sample, b_idx)
    last = np.append(last[-(l_X + l_label) * N:], greed)  # update last

print "the percision is ", correct / len(Y_test) * 100
