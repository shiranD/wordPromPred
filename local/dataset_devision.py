import numpy as np
from win_online import load_data
from random import sample

def construct_dataset(data_path):
    # creating a label corpus and an obs corpus
    # deviding them to train and test
    data_path = '../out_52947'
    all_data, bounds = load_data(data_path)  
    dict_y_train = {}
    dict_X_train = {}
    dict_y_test = {}
    dict_X_test = {}
    
    k=0
    j=0
    num_of_utt = 50
    # split to twx sets
    test_index = sample(range(num_of_utt), int(0.2*num_of_utt))
    for i in xrange(len(bounds)-1):
        if i in test_index:
            dict_y_test[k]=all_data[bounds[i]:bounds[i+1], -1]
            dict_X_test[k]=all_data[bounds[i]:bounds[i+1],:-1]        
            k+=1
        else:
            dict_y_train[j]=all_data[bounds[i]:bounds[i+1], -1]
            dict_X_train[j]=all_data[bounds[i]:bounds[i+1],:-1]
            j+=1
            
    return dict_X_test, dict_y_test, dict_X_train, dict_y_train

def concat_set(dict_X_test, dict_y_test):
    num_of_utt = 50
    k = int(0.2*num_of_utt)
    
    # concat the test
    for i in xrange(k):
        if i == 0:
            test_X = dict_X_test[0]  
            test_y = dict_y_test[0] 
            continue        
        test_X = np.concatenate((test_X, dict_X_test[i]), axis=0)
        test_y = np.concatenate((test_y, dict_y_test[i]), axis=0)
        
        return test_X, test_y

def shuffle_set(dict_X_train, dict_y_train):
    
    num_of_utt = 50
    
    # shuffle the train
    train_suf = np.random.permutation(num_of_utt-int(0.2*num_of_utt))
    yes = 1
    for i in train_suf:
        if yes:
            train_X = dict_X_train[0]  
            train_y = dict_y_train[0] 
            yes = 0
            continue        
        train_X = np.concatenate((train_X, dict_X_train[i]), axis=0)
        train_y = np.concatenate((train_y, dict_y_train[i]), axis=0)
        
    return train_X, train_y
    
    
