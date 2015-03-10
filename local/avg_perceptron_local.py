from __future__ import division
from collections import defaultdict
from dataset_devision import construct_dataset, concat_set, shuffle_set 
import numpy as np
import random 

        
def score_all(weights, sample):
    res = np.dot(weights,sample)
    max_value = max(res)
    idx = np.where(res==max_value)[0]
    if len(idx)>1:
        i = random.choice(idx)
        return max_value, int(i)
    else:      
        return max_value, int(idx)
          
data_path = '../out_52947'
dict_X_test, dict_y_test, dict_X_train, dict_y_train = construct_dataset(data_path)

num_iter = 2
count = 1
N = 2
# local will take only feats
x_size = len(dict_X_test[0][0])

weight = np.zeros((3, x_size*(N+1)),dtype=float)
weight_sum = np.zeros((3, x_size*(N+1)),dtype=float)

for it in xrange(num_iter):
    
    X_train, Y_train = shuffle_set(dict_X_train, dict_y_train)
    len_t = len(Y_train)      
        
    # TRAIN
    last = np.zeros(x_size*N)
    for (sample, label) in zip(X_train,Y_train):
        
        APsample = np.append(last[-(x_size*N):], sample)# take X last obs  
        product, p_idx = score_all(weight, APsample)# 3*len(APsample) dot product 

        if p_idx!=label-1:
            weight[label-1]+=(label-1-p_idx)*APsample
            weight[p_idx]-=(label-1-p_idx)*APsample # true value
       
            
        # hmm memory
        last = np.append(last[-(x_size*N):], sample)# update last
        count+=1 # update count            
    
        
# TEST
    
X_test, Y_test = concat_set(dict_X_test, dict_y_test)
correct = 0
last = np.zeros(x_size*N) 

for sample, label in zip(X_test,Y_test):
        
    APsample = np.append(last[-(x_size*N):], sample)  
    product, p_idx = score_all(weight, APsample)# 3*len(APsample) dot product            
                   
    if p_idx==label-1:   
        correct+=1
        print p_idx
    last = np.append(last[-(x_size*N):], sample)
        
print "the percision is ", correct/len(Y_test)*100