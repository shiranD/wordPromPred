def comute_final(dur_mat, num_mat, den_sum):
    
    """compute the frame level ratio between numerator
    to denominator. sum up per numerator duration (representing 
    a phoneme)"""
    
    ratio = num_mat[:,1]/den_sum # logadd
    durs = dur_mat[:,2]
    begin = 0
    tot_summ = []
    pdf_id = []
    for dur in durs:
        end = begin+dur
        seg_ratio = ratio[begin:end]
        summ = 0
        for val in seg_ratio:
            summ+=val
        tot_summ.append(summ)
        pdf_id.append(num_mat[begin,0])
        begin = end
        
    return pdf_id, tot_summ
