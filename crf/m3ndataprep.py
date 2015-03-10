from dataPrep import k_fold_cross_validation

path = '../out_85175'
l = 0

for i, (X_train, y_train, X_test, y_test) in enumerate(k_fold_cross_validation(path, 10,randomize=True)):
    f1 = open("sets1/"+str(i)+".train","w")
    f2= open("sets1/"+str(i)+".test","w")
    
    for X_seq, y_seq in zip(X_train, y_train):
        
        for obs, tag in zip(X_seq, y_seq):  
            lis = obs
            # extract token
            w = lis[1]
            token = w.split("=")[1]
            
            while len(lis)<24:
                obs.append(" ")
                lis = obs
                                    
            OBS = str(obs)[1:-2]
            OBS.replace(","," ")
            
            
                
            line = token+"\t"+OBS+"\t"+tag
            f1.write(line)
            f1.write("\n")
            
    f1.close()
    
            
    for X_seq, y_seq in zip(X_test, y_test):
        
        for obs, tag in zip(X_seq, y_seq):  
            lis = obs
            # extract token
            w = lis[1]
            token = w.split("=")[1]
            
            while len(lis)<24:
                obs.append(" ")
                lis = obs+[tag]
                                    
            OBS = str(obs)[1:-1]
            OBS.replace(","," ")
            
            line = token+"\t"+OBS+"\t"+tag
            f2.write(line)
            f2.write("\n")
            
    f2.close()

    