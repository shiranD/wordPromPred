from __future__ import division

import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

def wilson(n,p,z):
    nith = 1 / n
    zqr = z*z
    scalar = 1 / (1 + nith * zqr)
    tail = z * np.sqrt(nith * p * (1-p) + 1 / 4 * nith * nith * zqr)
    head = p + 1 / 2 * nith * zqr
    pos = scalar * (head + tail)
    neg = scalar * (head - tail)
    return pos, neg, scalar * head, scalar * tail

num_obs = 10000
z_val = 1.9599639845400538273879

acc = 0.786
#print acc, wilson(num_obs, acc, z_val)

acc = [0.699,0.727, 0.738, 0.766, 0.775, 0.786]
heads = []
tails = []
for ac in acc:
    _,_,head, tail = wilson(num_obs, ac, z_val)
    heads.append(head)
    tails.append(tail)


fig = plt.figure()
ax = fig.add_subplot(111)
ax.errorbar([0,1,2,3,4,5], heads, yerr = tails, fmt = 'o')
plt.xlim([-1,6])
plt.title("Wilson Score Interval")
plt.xlabel("trial")
plt.ylabel("accuracy")
plt.xticks(range(len(heads)),\
           ['Baseline', 'clp tg', 'Word','clp tg\n+ word','phrases\n+ word','phrases\n+ word+syll\n + kon+ cls tg'],\
           color='magenta')
ax.grid()
#plt.show()
plt.savefig("wilson")