from dataPrep import k_fold_cross_validation
import numpy as np

path = '../out_85175'
l = 0
non = ""
ft_num = 12
seq_num = 61
for i in range(ft_num):
    non+=" \t"

#print len(non.split("\t"))
SHir = []
for i, (X_train, y_train, X_test, y_test) in enumerate(k_fold_cross_validation(path, 10,randomize=True)):
    f1 = open("sets/"+str(i)+".train","w")
    f2= open("sets/"+str(i)+".test","w")
    for X_seq, y_seq in zip(X_train, y_train):
        #print len(X_seq)
        

        nX_seq = []
        for o in X_seq:            
            while len(o)<ft_num:
                o.append(" ")
            nX_seq.append(o)
         
        # all obs
        all_obs_feat = ""                
        for o in nX_seq:            
            for feat in o:
                all_obs_feat+=str(feat)+"\t"
        
        # right amount of obs
        if len(nX_seq)<seq_num:
            for i in xrange(seq_num-len(nX_seq)):
                
                all_obs_feat+=non  
                
        
        for obs, tag in zip(nX_seq, y_seq):  
            # extract token
            w = str(obs[0])
            token = w.split("=")[1]
            
            while len(obs)<ft_num:
                obs.append(" ")
                
            o_feat = ""
            for feat in obs:
                if "word" == str(feat)[:4]:
                    continue
                o_feat+=str(feat)+"\t"
                                    

             
            line = token+"\t"+o_feat+all_obs_feat+tag            
            f1.write(line)
            f1.write("\n")
            
    f1.close()
    
            
    for X_seq, y_seq in zip(X_test, y_test):
        SHir.append(len(X_seq))
        
     
        nX_seq = []
        for o in X_seq:            
            while len(o)<ft_num:
                o.append(" ")
            nX_seq.append(o)
                       
                        
        # all obs
        all_obs_feat = ""                        
        for o in nX_seq:
            for feat in o:
                all_obs_feat+=str(feat)+"\t"
        
        # right amount of obs
        if len(nX_seq)<seq_num:
            for i in xrange(seq_num-len(nX_seq)):
                all_obs_feat+=non  
                
        
        for obs, tag in zip(nX_seq, y_seq):  
            # extract token
            w = str(obs[0])
            token = w.split("=")[1]
            
            while len(obs)<ft_num:
                obs.append(" ")
                
            o_feat = ""
            for feat in obs:
                if "word" == str(feat)[:4]:
                    continue
                o_feat+=str(feat)+"\t"
                                    

             
            line = token+"\t"+o_feat+all_obs_feat+tag            
            f2.write(line)
            f2.write("\n")
            
    f2.close()

#print "s"
print np.bincount(SHir)