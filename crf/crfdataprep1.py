from dataPrep import k_fold_cross_validation

path = '../out_85175'
l = 0

for i, (X_train, y_train, X_test, y_test) in enumerate(k_fold_cross_validation(path, 10,randomize=True)):
    f1 = open("sets/"+str(i)+".train","w")
    f2= open("sets/"+str(i)+".test","w")
    
    for X_seq, y_seq in zip(X_train, y_train):

        o_str = ""
        for o in X_seq:
            while len(o)<24:
                o.append(" ")
            OBS = str(o)[1:-1]
            OBS = OBS.replace(","," ")
            o_str+=OBS+"\t"
            
        if len(X_seq)<61:
            for i in xrange(61-len(X_seq)):
                o_str+=" \t"        
        
        for obs, tag in zip(X_seq, y_seq):  
            # extract token
            w = obs[1]
            token = w.split("=")[1]
            
            while len(obs)<24:
                obs.append(" ")
                                    
            OBS = str(obs)[1:-1]
            OBS = OBS.replace(","," ")
             
            line = token+"\t"+OBS+"\t"+o_str+tag            
            f1.write(line)
            f1.write("\n")
            
    f1.close()
    
            
    for X_seq, y_seq in zip(X_test, y_test):
     
        o_str = ""
        for o in X_seq:
            while len(o)<24:
                o.append(" ")
            OBS = str(o)[1:-1]
            OBS = OBS.replace(","," ")            
            o_str+=OBS+"\t"
            
        if len(X_seq)<61:
            for i in xrange(61-len(X_seq)):
                o_str+=" \t"
            
        
        for obs, tag in zip(X_seq, y_seq):  
            # extract token
            w = obs[1]
            token = w.split("=")[1]
            
            while len(obs)<24:
                obs.append(" ")
                                    
            OBS = str(obs)[1:-1]
            OBS = OBS.replace(","," ")
            
            line = token+"\t"+OBS+"\t"+o_str+tag
            f2.write(line)
            f2.write("\n")
            
    f2.close()

