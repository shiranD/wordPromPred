from __future__ import division

from grep import locate_file
import numpy as np
from math import log, exp

FMAX = 1.79e308
FMIN = -FMAX
FEPS = 2.3e-16
ZMIN = np.log(np.exp(FEPS) - 1.0) # because: log(1+exp(-37)) = 0, but log(1+exp(-36)) = 2e-16
assert log(1+exp(ZMIN)) > 0
ZMAX = np.log(FMAX - 1.0) # because 1+exp(709) is near inf
assert exp(ZMAX) / FMAX > 1 - 1e-6 # we are very near the overflow


def check_grp(segm):
    
    # make list of pdf-dur
    pd_dur = []
    old_pd = -1
    dur = -1
    for pd in segm:
        if pd!=old_pd:
            pd_dur.append([old_pd,dur])
            dur = 1
            old_pd = pd
        else:
            dur+=1
    pd_dur.append([pd,dur])
    pd_dur=pd_dur[1:]
    
    # check grp and merge
    q_pair = []
    for pdf, dur in pd_dur:
        if pdf in [0,1,2,3,4,5]: # sil states
            quotient = 0
        else:           
            quotient = np.floor(pdf/3)
        q_pair.append([quotient, pdf, dur])
        
    # grouping up same phoneme pdf_ifs    
    old_q=-1
    pair_s = []
    for i, (q, pdf, dur) in enumerate(q_pair):
        if old_q==q:
            [du], idx= pair_s[-1]
            idx.append(i)
            du+=dur
            pair_s[-1] = [[du], idx]
        else:
            pair_s.append([[dur], [i]])
        old_q=q
        
    # choose max grp dur
    dur_max = 0
    pairs_list = []
    for it in xrange(len(pair_s)):
        dur=pair_s[it][0][0]
        if dur > dur_max:
            indx = pair_s[it][1]
            dur_max = dur
    for ind in indx:
        pairs_list.append(pd_dur[ind])
        
    begin = 0
    
    # begin idx
    for i in xrange(indx[0]):
        begin += q_pair[i][2]
        
    assert dur_max+begin <= len(segm)

    return dur_max, begin   
    

def log_add(a, b):
    """returns log(exp(a) + exp(b)) =
    log(x+y) = log(x) + log(1 + exp(log(y)-log(x)))
    = a + log(1+exp(b-a))
    where a = log(x), b = log(y)"""
    assert np.isfinite(a+b)
    if a > b: # swap, so that a < b
        z = a; a = b; b = z
    z = a - b
    if z < ZMIN: # underflow or below minimum difference
        #print 'z underflow ', z
        return b # the greater of the two
    elif z < ZMAX:
        return b + log(1.0 + exp(z)) # normal case
    else:
        #print 'z overflow ', z                
        return b + ZMAX  
        

def compute_denominator(mat, uttfile, pdf, dur, dur_n, mode): 
    
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
        
        
    if mode == 1:
            
                
        # extract pdf corresponding to the mat
        sum_dur = np.zeros((len(dur_n),2))
        flag = 0    
        for line in open(pdffile).readlines():
            
            if uttfile in line:
                flag+=1          
            
            if flag == 1:
                pdf_ids = line.split(" ", 1)[1].split()
                pdf_ids = [int(o) for o in pdf_ids]
                assert sum(durs)==len(pdf_ids)
                begin = 0
                for i,seg in enumerate(dur_n):
                    end = begin+int(seg)
                    segment = pdf_ids[begin:end]# extract pdf_id
                    matseg = mat[begin:end] # extract ll
                    summ=0

                    for pdf_id, line in zip(segment,matseg):
                        summ+=line[pdf_id]     
                    sum_dur[i, 0] = summ/seg
                    sum_dur[i, 1] = seg # numerator dur 
                    begin = end
                break
        
        return sum_dur
        
    if mode == 2:
        
        
        # extract pdf corresponding to the mat
        sum_dur = np.zeros((len(dur_n),2))
        flag = 0    
        for line in open(pdffile).readlines():
            
            if uttfile in line:
                flag+=1          
            
            if flag == 1:
                pdf_ids = line.split(" ", 1)[1].split()
                pdf_ids = [int(o) for o in pdf_ids]
                assert sum(durs)==len(pdf_ids)
                begin = 0
                for i,seg in enumerate(dur_n):
                    end = begin+int(seg)
                    segment = pdf_ids[begin:end]# extract pdf_id
                    dur_pd, b_idx = check_grp(segment)
                    # update segment,matseg
                    segment = pdf_ids[begin+b_idx:begin+b_idx+dur_pd]# extract pdf_id
                    
                    matseg =      mat[begin+b_idx:begin+b_idx+dur_pd] # extract ll
                    summ = 0                    
                    for pdf_id, line in zip(segment,matseg):
                        summ+=line[pdf_id]     
                    sum_dur[i, 0] = summ/dur_pd
                    sum_dur[i, 1] = int(dur_pd) # numerator dur 
                    begin = end
                break
            
        return sum_dur
            
    
    if mode == 3:

            

        
        tot_sum = []
        for line in mat:
            summ = 0  
            first = 1
            for val in line:
                if first:
                    summ = val
                    first = 0
                else:
                    summ = log_add(summ, val)
            tot_sum.append(summ)
        return tot_sum
    
        
        
        
        