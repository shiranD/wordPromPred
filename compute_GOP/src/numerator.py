from __future__ import division

from grep import locate_file
import numpy as np

def compute_numrator(mat, uttfile, pdf, dur, mode): 
    
    """extract the phd_id, its duration and the 
    sum of likelihood per duration. for ratio 
    GOP explanation beloow"""
    
    # locate utt in pdf and dur files
    durfile = locate_file(uttfile, dur)       
    pdffile = locate_file(uttfile, pdf) 
    
    # extract duration
    flag = 0
    durs = []  
    # dur is constrained to one line
    for line in open(durfile).readlines():
        
        if uttfile in line:
            flag+=1          
        
        if flag == 1:
            line = line.split("[", 1)[1]
            line = line.rsplit("]", 1)[0]            
            segms = line.split(" ] [ ")
            for seg in segms:
                seg = seg.split()
                l_seg = len([float(o) for o in seg])          
                durs.append(l_seg)
        if flag > 1:
            break
                
    # extract pdf corresponding to the mat
    phn_sum_dur = np.zeros((len(durs),3))
    flag = 0    
    for line in open(pdffile).readlines():
        
        if uttfile in line:
            flag+=1          
        
        if flag == 1:
            pdf_ids = line.split(" ", 1)[1].split()
            pdf_ids = [int(o) for o in pdf_ids]
            assert sum(durs)==len(pdf_ids)
            begin = 0
            summ = 0
            for i, seg in enumerate(durs):
                end = begin+seg
                segment = pdf_ids[begin:end]
                matseg = mat[begin:end]
                summ = 0                
                for pdf_id, line in zip(segment,matseg):
                    summ+=line[pdf_id]
                phn_sum_dur[i, 0] = segment[0]
                phn_sum_dur[i, 1] = summ
                phn_sum_dur[i, 2] = int(seg)
                begin = end
            break
            
    if mode==1 or mode==2:
        # normalize ll
        phn_sum_dur[:,1] = phn_sum_dur[:,1]/phn_sum_dur[:,2]
        
        return phn_sum_dur, []
    
    if mode==3:
        """extract likelihood per pdf_id"""
        flag = 0
        seq_ll = np.zeros((sum(durs),2))
        for line in open(pdffile).readlines():
            
            if uttfile in line:
                flag+=1          
            
            if flag == 1:
                pdf_ids = line.split(" ", 1)[1].split()
                pdf_ids = [int(o) for o in pdf_ids]
                assert sum(durs)==len(pdf_ids)
                for i,(line, pd) in enumerate(zip(mat,pdf_ids)):
                    #if pd > 123:
                     #   pd=122
                    seq_ll[i,0]=pd
                    seq_ll[i,1]=line[pd]
                break   
        
        return phn_sum_dur, seq_ll
    
        
        
        
        