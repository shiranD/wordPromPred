from __future__ import division
from math import sqrt
from scipy.stats import chi2_contingency,chi2
import numpy as np

if 0:
    acc = [0.699,0.727, 0.738, 0.766, 0.775, 0.786]
    
    twenyk = 20000
    for i in xrange(len(acc)-1):
        p1 = acc[i]
        p2 = acc[i+1]
        a = chi2_contingency(np.array([[twenyk*p1, twenyk - twenyk*p1], [twenyk*p2, twenyk - twenyk*p2]]))        
        print p1,p2,a[1]
    
    
    def two_prop(k1, k2, n1, n2):
        phat1 = k1/n1
        phat2 = k2/n2
        phat = (k1+k2)/(n1+n2)
        numerator = phat1 - phat2
        denominator = sqrt(phat*(1-phat)*(1/n1+1/n2))
        return numerator/denominator
    print two_prop(0.783*twenyk ,0.699*twenyk, twenyk, twenyk)
    
if 1:
    acc = [0.727, 0.738, 0.766, 0.775, 0.786]
    y_n = [[0.727-0.1,0.1],[0.738-0.1,0.1],[0.766-0.1,0.1],[0.775-0.1,0.1],[0.786-0.1,0.1]]
    twenyk = 20000
    for i in xrange(len(acc)-1):
        p1 = acc[i]
        p2 = acc[i+1]
        
        a1 = y_n[i][0]*twenyk
        a2 = y_n[i][1]*twenyk
        b1 = y_n[i+1][0]*twenyk
        b2 = y_n[i+1][1]*twenyk
        if a1>b1:
            a = b1
            c = a1-b1
        else:
            a = a1
            c = b1-a1
        if a2>b2:
            d = b2
            b = a2-b2
        else:
            d = a2
            b = b2-a2
            
        stat = (b-c)**2/(b+c)# asymptotic
        df = 1
        pval = chi2.sf(stat, df)
        print chi_2, pval        
        
if 1:# http://en.wikipedia.org/wiki/McNemar%27s_test
    b = 6
    c = 16
    stat = (b-c)**2/(b+c) # asimptotic test
    stat = (np.abs(b-c)-1)**2/(b+c)# continuity test        
    df = 1
    pval = chi2.sf(stat, df)  
    print pval
    #http://statsmodels.sourceforge.net/devel/_modules/statsmodels/sandbox/stats/runs.html#mcnemar
    #stat = (np.abs(b-c)-1)**2/(b+c)                        
    #pval = stats.binom.cdf(stat, n1 + n2, 0.5) * 2    
    