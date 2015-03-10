from grep import locate_file

def load_likelihood(uttfile, likefiles):
    """extract likelihood matrix for utterance
    every line is a frame, every line componenet
    is pdf-id"""
    
    # locate utt in likefiles
    likefile = locate_file(uttfile, likefiles)
    
    # extract lines
    flag = 0
    likemat = []    
    for line in open(likefile).readlines():
        
        if flag:
            if "]" in line: # end of utt
                line = line.replace(" ]","")
                likes = line.split()
                likes = [float(o) for o in likes] 
                likemat.append(likes)
                
                flag = 0 # finished
                break
            likes = line.split()
            likes = [float(o) for o in likes]            
            likemat.append(likes)
            
        if uttfile in line:
            flag = 1
            
    #open next file if needed
    if flag:
        num = likefile.split(".")[-2]
        num = int(num)+1
        chunk = likefile.split("s.")
        #modify likefile
        likefile = chunk[0]+"s."+str(num)+".txt"
        
        for line in open(likefile).readlines():
            
            if "]" in line: # end of utt
                line = line.replace(" ]","")
                likes = line.split()
                likes = [float(o) for o in likes]                 
                break         
            likes = line.split()
            likes = [float(o) for o in likes]            
            likemat.append(likes)            
                
    return likemat