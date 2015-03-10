from __future__ import division
from collections import defaultdict
from dataset_devision import construct_dataset, concat_set, shuffle_set 
import numpy as np
import random 

def make_last(hmm_order, feat_size):
    
    pre_samples = []
    feat = np.zeros(feat_size, dtype=int)
    label = np.zeros(3,dtype=int)
    label[2] = 1  # common_class_label = 3        
    for i in xrange(hmm_order):
        pre_samples.extend(feat)
        pre_samples.extend(label)
        
    return pre_samples        

def score_all(weights, sample):

    res = np.dot(weights,sample)
    idx = np.argmax(res)
    max_value = res[idx]
    idx_2 = np.zeros(3)
    idx_2[idx]=1
    return max_value, idx, idx_2

data_path = '../out_85175'
dict_X_test, dict_y_test, dict_X_train, dict_y_train = construct_dataset(data_path)

num_iter = 20
count = 1
N = 2
num_clas = 3
l_label = 3
# local will take only feats
l_X = len(dict_X_test[0][0])
weight = np.zeros((num_clas, (l_X+l_label)*(N+1)-l_label),dtype=float)
weight_sum = np.zeros((num_clas, (l_X+l_label)*(N+1)-l_label),dtype=float)

for it in xrange(num_iter):
    
    X_train, Y_train = shuffle_set(dict_X_train, dict_y_train)# in place
    len_t = len(Y_train)       

    # TRAIN
    last = make_last(N, l_X)
    for (sample, label) in zip(X_train,Y_train):
        
        APsample = np.append(last[-(l_X+l_label)*N:], sample)# take X last obs  
        product, p_idx, b_idx = score_all(weight, APsample)# 3*len(APsample) dot product 

        if p_idx!=label-1:
 
            weight[label-1]+=(label-1-p_idx)*APsample # make sure this update is ok!
            weight[p_idx]-=(label-1-p_idx)*APsample # true value             
            
        # hmm memory
        greed = np.append(sample, b_idx)
        last = np.append(last[-(l_X+l_label)*N:],greed)# update last
        #average and incourage
        weight_sum+=(weight-weight_sum)/count   
        count+=1 # update count         
        
        
    
        
# TEST
    
X_test, Y_test = concat_set(dict_X_test, dict_y_test)
correct = 0
last = make_last(N,l_X)
for sample, label in zip(X_test,Y_test):
        
    APsample = np.append(last[-(l_X+l_label)*N:], sample)# take X last obs  
    product, p_idx, b_idx = score_all(weight_sum, APsample)# 3*len(APsample) dot product            
                   
    if p_idx==label-1:   
        correct+=1
        print p_idx
    greed = np.append(sample, b_idx)        
    last = np.append(last[-(l_X+l_label)*N:], greed)# update last
        
print "the percision is ", correct/len(Y_test)*100