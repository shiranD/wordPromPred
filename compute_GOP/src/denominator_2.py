from grep import locate_file
import numpy as np
from math import log, exp


#den_norm_sum, dur_m = compute_denominator(ll_mat, filename, bestfiles, ph_sum_dur[:,2], mode)# number of frames

def check_grp(pairs):
    old_quotient = -1
    q_pair = []

    for pdf, dur in pairs:
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
        
    # choosing the max duration segment    
    dur_max = 0
    pairs_list = []
    for it in xrange(len(pair_s)):
        dur=pair_s[it][0][0]
        if dur > dur_max:
            indx = pair_s[it][1]
            dur_max = dur
    for ind in indx:
        pairs_list.append(pairs[ind])
    return pairs_list, dur_max
            

def compute_denominator(mat, uttfile, best, durs , mode):
    
    # locate utt in 1best files
    bsetfile = locate_file(uttfile, best)
    
    # extract lines
    flag = 0
    pdf_dur_best = []   
    for line in open(bsetfile).readlines():
        
        # assuming filenames contain "_"            
        if  flag and "_" not in line:
            if "," in line: # 84 85 0 0,0,26417\n
                continue
            flag = 0 # 86\n
            break        
        
        if flag:

            line = line.replace("\t",",")
            chunks = line.split(",") 
            pdf = int(chunks[2])
            len_pdf = len(chunks[-1].split("_"))-1
            pdf_dur_best.append([pdf, len_pdf])
            
                        
        if uttfile in line:
            flag = 1

            
    #open next file if needed
    if flag:
        num = bsetfile.split(".")[1]
        num = int(num)+1
        #modify bsetfile name
        bsetfile = "lat."+num+".phone.1best"
        
        for line in open(bsetfile).readlines():
            
            # assuming filenames contain "_"            
            if "_" not in line:
                flag = 0
                break              
                     
            line = line.replace("\t",",")
            chunks = line.split(",")
            pdf = int(chucks[2])
            len_pdf = len(chunks[-1].split("_"))-1
            pdf_dur_best.append([pdf, len_pdf]) 
            
    # construct a frame pdf candidates
    pair_dict = {}# order stays in append for computing
    for i,dur in enumerate(durs):
        tot = dur
        frame_pdf_cand = []
        for k,(pdf,dpdf) in enumerate(pdf_dur_best):
            
            if tot <= 0:
                break
            frame_pdf_cand.append([pdf,int(min(dpdf,tot))])            
            tot-= dpdf
            last_pdf=pdf
        pair_dict[i]=frame_pdf_cand
        # update( delete the used frames)
        pdf_dur_best=pdf_dur_best[k:]
        if tot!=0:
            pdf_dur_best=[[last_pdf, int(-tot)]]+pdf_dur_best
            
        
    # GOP SUM - sum up all frame per likelihood pdf-id
    # output: nomalized sum
    if mode == 1:
        begin = 0 
        tot_sum = []
        for i,dur in enumerate(durs):
            end = begin+int(dur)
            mat_segment = mat[begin:end]
            begin = end
            j=0
            summ = 0
            for pd, durr in pair_dict[i]:
                for d in xrange(durr):
                    if pd> 122: # take off when correct file exist
                        pd=122
                    summ = mat_segment[j][pd]
                    j+=1
            tot_sum.append(summ/durs[i])   
        return tot_sum, []
        
    # GOP MAX - take pdf_id with max duration
    # output: nomalized sum, with pdf_id
    if mode == 2:
        begin = 0 
        tot_sum = []
        new_dict = {}
        dur_m = []
        for i,dur in enumerate(durs):
            end = begin+int(dur)
            mat_segment = mat[begin:end]
            begin = end
            j=0
            summ = 0
            # check if pdf_id are of the same phoneme, choose max
            pairs, dur_max = check_grp(pair_dict[i])
            #pairs = check_grp(pair_dict[i])
            
                    
            for pd, durr in pairs:
                for d in xrange(durr):
                    if pd> 122: # take off when correct file exist
                        pd=122
                    summ = mat_segment[j][pd]
                    j+=1
            tot_sum.append(summ/dur_max)
            dur_m.append(dur_max)
            new_dict[i] = pairs
            
        # return new_dict
        return tot_sum,dur_m
    
    # GOP - posterior one over all
    if mode == 3:
        
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
            
        FMAX = 1.79e308
        FMIN = -FMAX
        FEPS = 2.3e-16
        ZMIN = np.log(np.exp(FEPS) - 1.0) # because: log(1+exp(-37)) = 0, but log(1+exp(-36)) = 2e-16
        assert log(1+exp(ZMIN)) > 0
        ZMAX = np.log(FMAX - 1.0) # because 1+exp(709) is near inf
        assert exp(ZMAX) / FMAX > 1 - 1e-6 # we are very near the overflow
        
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
        return tot_sum, []

            
    
        
