#! /opt/local/bin/python -O
# viterbi.py: simple Viterbi decoding, with protections against underflow
# Steven Bedrick <bedricks@ohsu.edu> and Kyle Gorman <gormanky@ohsu.edu>

from __future__ import division
from bitweight import BitWeight
from numpy import array, int8, ones, zeros, empty
from ngrammodel import MaximumLikelihoodNGramModel
from collections import Counter
from dataset_devision import construct_dataset, make_train, make_test
import copy
import numpy as np
   

def create_local_emissions(emissions_dict,state_lookup_backwords,observation):
    emissions = np.zeros((len(state_lookup_backwords)-1,len(observation)),dtype = BitWeight)# don't include s_0
    i = 0
    for word in observation: # check
        j = 0
        for po, wos in emissions_dict:
            for wo in wos:
                if wo == word:
                    n_pre = re.findall('\(\'(\S{1,30})\'\,\)',str(po))
                    if n_pre: # for word
                        pos_ind = state_lookup_backwords[n_pre[0]] - 2
                        emissions[pos_ind, i] = emissions_dict[j][1][wo] 
                    else:
                        ch = str(po) # for ch 
                        ch = ch[2:-3]
                        pos_ind = state_lookup_backwords[ch] - 2
                        emissions[pos_ind, i] = emissions_dict[j][1][wo]                         
                        
            j+=1
        i+=1
    return emissions
                
    

    
def dict_to_list(t_dict):
    # convert dict to matrix
    t_matrix = np.zeros((len(t_dict), len(t_dict)),dtype = BitWeight)
    
    for (key,), value in t_dict.iteritems():
        if len(key)!=1:
            continue
        pre = int(key)-1
        for suf, val in value.iteritems():
            if len(suf)!=1:
                continue            
            suf = int(suf)-1
            t_matrix[pre,suf] = val
            print pre , suf
            
    return t_matrix
            
def obs_hidd_corpus(hid, ob):
    # create all couples of ob-hid from train
    couples = []
    for hid_seq, ob_seq in zip(hid, ob):
        for hid_unit, ob_unit in zip(hid_seq, ob_seq):
            couples.append([hid_unit, ob_unit])
    return couples
            
     

def create_po_corpus(text_corpus, num):
    if num==1:
        sentences = [line.rstrip() for line in text_corpus]
    else:
        sentences = text_corpus
        
    f1 = open('pos_sentence.txt','w')
    for sentence in sentences:       
        #reg1 = re.findall('\/(\w{1,30})\|?',sentence)
        reg1 = re.findall('\/(\S{1,4})\s' ,sentence) 
        temp = ' '.join(reg1)
        f1.write(temp) 
        f1.write('\n') 
        if 0:#num != 1:
            temp = ' '.join(reg2)
            f1.write(temp) 
            f1.write('\n')
    f1.close()
    po_sen = [line.rstrip() for line in open('pos_sentence.txt','r')]
    po_corpus = [line.split() for line in po_sen]  
    return po_corpus



def to_real_V(vec):
    v = np.zeros(len(vec))
    for i in xrange(len(vec)):
        if vec[i]!=0:
            v[i] = vec[i].to_real
    return v

def viterbi(observations, states, transitions, emissions, state_lookup_backwords,transitions_1_dict):
    """
    Compute best path (in the form of a state sequence) through an HMM 
    (represented by the tuple of observations, states, the transition 
    matrix (conditional probability of a state given the previous state), 
    and the emission matrix (conditional probability of a token given the 
    hidden state)
    """
    l_e = len(  emissions[0, :])
    l_t = len(transitions[:, 0])                
            
    l_e = len(  emissions[0, :])
    l_t = len(transitions[:, 0])
    vi = zeros((l_t -1, l_e),dtype = BitWeight)
    backpointer = zeros((l_t-1, l_e),dtype = BitWeight)
    vi[:,0] = transitions[0, :] * emissions[:, 0]
    for i in xrange(1,l_e):
        flag = 0
        for state in states:
            ind2 = state_lookup_backwords[state]
            vi[int(ind2)-2, i] =  BitWeight(np.max(to_real_V(vi[:,i-1]) * to_real_V(transitions[1:,int(ind2)-2]))) * emissions[int(ind2)-2, i]                
            if vi[int(ind2)-2, i].to_real!=0:
                backpointer[int(ind2)-2, i-1] = np.argmax([to_real_V(vi[:,i-1]) * to_real_V(transitions[1: ,int(ind2)-2])])+1 # -2=-1 for ofbyone -1 elimiate s_0
                flag = 1
        if flag == 0: # there's no tag related to the current word
            chosen_tag = 'NN'
            ind = state_lookup_backwords[chosen_tag]
            emissions[:,i] = BitWeight(1.0)            
            for state in states:
                ind2 = state_lookup_backwords[state]
                vi[int(ind2)-2, i] =  BitWeight(np.max(to_real_V(vi[:,i-1]) * to_real_V(transitions[1: ,int(ind2)-2]))) * emissions[int(ind2)-2, i]
                if vi[int(ind2)-2, i].to_real!=0:
                    backpointer[int(ind2)-2, i-1] = np.argmax([to_real_V(vi[:,i-1]) * to_real_V(transitions[1: ,int(ind2)-2])])+1 # -2=-1 for ofbyone -1 elimiate s_0
                    flag = 1            
        if flag == 0:
            for state in state:
                for prefix, sufixes in transitions_1_dict:
                    for sufix in sufixes:
                        if sufix == state: #back off
                            ind2 = state_lookup_backwords[state]
                            vi[int(ind2)-2, i] =  BitWeight(np.max(to_real_V(vi[:,i-1]) * transitions_1_dict[0][1][sufix].to_real)) * emissions[int(ind2)-2, i]
                            if vi[int(ind2)-2, i].to_real!=0:
                                backpointer[int(ind2)-2, i-1] = np.argmax(to_real_V(vi[:,i-1]) * transitions_1_dict[0][1][sufix].to_real)+1 # -2=-1 for ofbyone -1 elimiate s_0
                                flag = 1   
                
            
            
            
    backpointer[0,i] = np.argmax(to_real_V(vi[:,i]))+1

    #print backpointer
    #print vi  
    
    t = []
    for i in xrange(len(backpointer[:,-1])): # find the last PoS
        if not(backpointer[i,-1]):
            continue
        else:
            t = np.append(t, backpointer[i,-1])
            break
        
    for h in xrange(l_e-1):
        if backpointer[int(t[h]-1), int(l_e-2-h)]:          
            t = np.append(t, backpointer[int(t[h]-1), int(l_e-2-h)]) # concat according to pointers
        else:                      
            a = np.where(backpointer[:,int(l_e-2-h)]!=0)
            t = np.append(t, a[0][0])
            
        
    return t[::-1]
    #return sequence


if __name__ == "__main__":
    
    
    data_path = '../out_52947'    
    dict_X_test, dict_y_test, dict_X_train, dict_y_train = construct_dataset(data_path)
    obs_corpus, hid_corpus, codebook = make_train(dict_X_train, dict_y_train)
    obs_corpus = copy.deepcopy(hid_corpus)
    hid_ob_corpus = obs_hidd_corpus(hid_corpus, obs_corpus)
    
    # test:   
    # upload test_y test_X 
    # convert test obs according to codebook
    #obs_test, hid_test = make_test(dict_X_test, dict_y_test, codebook)

    
    transitions_dict = MaximumLikelihoodNGramModel(hid_corpus,2).prob.items() # transitions_dict
    #emissions_dict = MaximumLikelihoodNGramModel(hid_ob_corpus,2).prob.items() # emissions_dict
    transitions_1_dict = MaximumLikelihoodNGramModel(hid_corpus,1).prob.items() # transitions_dict  
        
    transitions = dict_to_list(dict(transitions_dict))

        
    t = 0
    acc = 0    
    confusion_mat = np.zeros((len(states) -1,len(states)-1))
    
    for observation in obs_test:
        emissions = create_local_emissions(emissions_dict,state_lookup_backwords, observation) # from emission_dict
        sequence = viterbi(observation, states[1:], transitions[:,:-1], emissions, state_lookup_backwords,transitions_1_dict)
        print ' '.join(state_lookup[i] for i in sequence)        
        ac = 0        
        for segment in hid_test:
            i = 0
            for pos in segment:
                if i==len(sequence):
                    break
                if state_lookup[int(sequence[i])]!=pos:
                    num_ref = state_lookup_backwords[pos] # find the PoS key
                    confusion_mat[int(sequence[i]-2),num_ref-2]+=1 # populate confusion matrix (get dicrt inx add 2)
                else:
                    ac+=1
                    acc += ac / len(observation) # for accuracy
                i+=1

    print acc