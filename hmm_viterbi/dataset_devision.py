import numpy as np
from win_online import load_data
from random import sample
from scipy.cluster.vq import kmeans, vq
from sklearn.cluster import KMeans

def construct_dataset(data_path):
    # creating a label corpus and an obs corpus
    # deviding them to train and test
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
    
def make_train(dict_X_train, dict_y_train):
    # create labeled obs courpus and labeled hidden corpus
    # according to thier sentences sequences
    
    num_of_utt = 50
    
    # shuffle the train
    train_suf = np.random.permutation(num_of_utt-int(0.2*num_of_utt))
    train_y = []
    yes = 1
    for i in train_suf:
        y = dict_y_train[i]
        y = [str(st) for st in y]
        train_y.append(y) 
        
        if yes:
            train_X = dict_X_train[0]  
            yes = 0
            continue         
        
        train_X = np.concatenate((train_X, dict_X_train[i]), axis=0)
    obs_corpus, code = hash_obs(train_X, train_y)

    return obs_corpus, train_y, code
    
def hash_obs(obs,train_y):
    # create VQ to map obs vectors to labels
    #obs = np.array([[0,1,0,0],[0,1,0,1],[0,1,1,1],[1,1,0,0],[1,0,1,0],[1,0,1,0]])    
    
    km_model = KMeans(n_clusters=len(obs), init='k-means++', n_init=10,\
           max_iter=300, tol=0.0001, \
           precompute_distances=True, verbose=0,\
           random_state=None, copy_x=True, n_jobs=4)
    km_model.fit(obs)
    x_labels = km_model.predict(obs)
    x_labels = list(x_labels)
                
    # to make similar struct to y
    hashed_X_train = []
    begin = 0
    for val in train_y:
        X = x_labels[begin:len(val)+begin]
        X = [str(st) for st in X]
        hashed_X_train.append(X)
        begin = len(val)  
        
    return hashed_X_train, km_model

def make_test(dict_X_test, dict_y_test, km_model):
    # create test; obs according to kmean model
    # and hiddens according to labels
    
    num_of_utt = 50
    k = int(0.2*num_of_utt)
    
    
    test_y = []
    test_X = []
    yes = 1
    for i in xrange(len(dict_y_test)):
        y = dict_y_test[i]
        y = [str(st) for st in y]
        x = dict_X_test[i]
        x_labels = km_model.predict(x)
        
        test_y.append(y)
        test_X.append(x_labels)        
        
        
    return test_X, test_y    
    
    
    
    
    
    
    
