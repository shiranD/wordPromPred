#Copyright (c) 2015 Shiran Dudy.
#All rights reserved.

#Redistribution and use in source and binary forms are permitted
#provided that the above copyright notice and this paragraph are
#duplicated in all such forms and that any documentation,
#advertising materials, and other materials related to such
#distribution and use acknowledge that the software was developed
#by the CSLU. The name of the
#CSLU may not be used to endorse or promote products derived
#from this software without specific prior written permission.
#THIS SOFTWARE IS PROVIDED ``AS IS'' AND WITHOUT ANY EXPRESS OR
#IMPLIED WARRANTIES, INCLUDING, WITHOUT LIMITATION, THE IMPLIED
#WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.

from ngrammodel import MaximumLikelihoodNGramModel
from dataPrep import data_prep
from bitweight import BitWeight
import bitweight
from numpy import log2

X_train, y_train, X_test, y_test = data_prep()  
trans = MaximumLikelihoodNGramModel(y_train,1).prob.items() # transitions 
trans = dict(trans)

if 1:
    ent = 0
    tran=dict(trans)
    for state in ["0","1","2"]:
        print tran[()][state].to_real
        a=tran[()][state].to_real
        ent +=a*log2(a)
    print "tag entropy per symbol is ", ent
    
trans = MaximumLikelihoodNGramModel(y_train,3).prob.items() # transitions 
trans = dict(trans)
if 1:
    ent = 0
    all_dist=[]
    for prefix in trans.iterkeys():
        (p2,p1)=prefix
        if p2=="<S_1>" or p1=="<S_1>" or p2=="<S_0>" or p1=="<S_0>" or p1=='</S_1>' or p2=='</S_1>':
            continue
        a = 0
        ent = 0
        for suffix in ["0","1","2"]:#,"<S_1>","</S_1>"
            if trans[prefix][suffix].to_real!=0:
    
                a = trans[prefix][suffix].to_real
                d = (prefix,suffix,a)
                all_dist.append(d)
                
                ent+= a*log2(a)
        print "the entropy for prefix ",prefix, " is ", ent
    
    #print a
if 0:
    ent = 0
    all_dist=[]
    for suffix in ["0","1","2"]:#,"<S_1>","</S_1>"   
        a = 0
        ent = 0
        for prefix in trans.iterkeys():
            (p2,p1)=prefix
            if p2=="<S_1>" or p1=="<S_1>" or p2=="<S_0>" or p1=="<S_0>" or p1=='</S_1>' or p2=='</S_1>':
                continue        
            if trans[prefix][suffix].to_real!=0:
    
                a = trans[prefix][suffix].to_real
                d = (prefix,suffix,a)
                all_dist.append(d)
                
                ent+= a*log2(a)
        print "the entropy for suffix ",suffix, " is ", ent
            
print "the entropy for prefix ",prefix, " is ", ent
print "the entropy for trinomial distribution is ", -log2(3)#1/18
for item in reversed(sorted(all_dist)):
    print item
