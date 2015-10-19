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


from __future__ import division
from nltk.tokenize import RegexpTokenizer
from nltk.tokenize import WhitespaceTokenizer
import numpy as np
import string
import json
import io
import sys 


# problem with conjugation
# need hist for that too without decomposing them
# but now works
ic_dict = {}

cong = []
all_tokens = 0
#create IC dict
#tokenizer = RegexpTokenizer(r'\w+')
tokenizer = WhitespaceTokenizer()
filename = "../Subtlex.US.txt"
for line in open(filename,"r").readlines():
    line = line.lower()
    line = line.strip()
    #line = line.replace("-"," ")
    #line = "self-support"
    line = ' '.join(word.strip(string.punctuation) for word in line.split())
    print tokenizer.tokenize(line)
    t_list = tokenizer.tokenize(line)
    
    for token in t_list:
        try:
            token = token.encode("ascii", "ignore").lower()
            #token = unicode(token, 'utf8')
            #token = token.encode('utf8')
            try:
                ic_dict[token]
                ic_dict[token]+=1
                
            except:
                ic_dict[token] = 1
                
            all_tokens+=1
        except:
            pass

final = {}
for key in ic_dict.iterkeys():
    final[key] = int(round(-np.log(ic_dict[key] / all_tokens)))
print max(final.values())

jsonfile = "../icJson"
with io.open(jsonfile, 'w', encoding='utf8') as json_file:
    data = json.dumps(final, ensure_ascii=False)
    json_file.write(unicode(data))    
    #json_file.write(json.dumps(final), ensure_ascii=False, encoding='utf8')