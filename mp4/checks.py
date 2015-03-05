from ngrammodel import MaximumLikelihoodNGramModel
from dataPrep import data_prep
from bitweight import BitWeight
import bitweight
from numpy import log2

X_train, y_train, X_test, y_test = data_prep()  
trans = MaximumLikelihoodNGramModel(y_train,3).prob.items() # transitions 
trans = dict(trans)

#for (t_2,t_1),a in trans.iterkeys():
ent = 0
all_dist=[]
for prefix in trans.iterkeys():
    (p2,p1)=prefix
    if p2=="<S_1>" or p1=="<S_1>" or p2=="<S_0>" or p1=="<S_0>":
        continue
    for suffix in ["0","1","2"]:#,"<S_1>","</S_1>"
        if trans[prefix][suffix].to_real!=0:
            #print "transition from ",prefix, "prefix to ",suffix," is ", trans[prefix][suffix]
            a = trans[prefix][suffix].to_real
            d = (a,prefix,suffix)
            all_dist.append(d)
            
            ent+= a*log2(a)
    
print "the entropy is", ent
print "the entropy for trinomial distribution is ", log2(0.05)#1/18
for item in reversed(sorted(all_dist)):
    print item
