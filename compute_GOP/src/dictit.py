from __future__ import division
import numpy as np

def dict_phones(phonefile):
    phone = {}
    for line in open(phonefile).readlines():
        phon, num = line.split()
        if num == "0":
            phone[num] = "sil"
            continue
            
        phone[num] = phon
    return phone
        
def dict_pdfs(pdf2numfile):
    
    pdfs = {}
    for line in open(pdf2numfile).readlines():
        num, _, pdf = line.split()
        pdfs[int(pdf)] = num
        
    return pdfs
        
        
    
    