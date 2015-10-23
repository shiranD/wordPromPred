#! /opt/local/bin/python -O
# MP4 skeleton implementation
# Kyle Gorman <gormanky@ohsu.edu>
# taken from NLP class at OHSU from http://www.cslu.ogi.edu/~gormanky/courses/CS662/
# this code was modifed by Shiran Dudy <dudy@ohsu.edu>

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

#/usr/bin/python
# -*- coding:utf-8 -*-
states = ('Rainy','Sunny')
observations = ('walk','shop','clean')
start_probability = {
    'Rainy|Rainy':0.7,
    'Rainy|Sunny':0.3,
    'Sunny|Rainy':0.4,
    'Sunny|Sunny':0.6
}
transition_probability = {
    'Rainy|Rainy' : {'Rainy':0.8,'Sunny':0.2},
    'Rainy|Sunny' : {'Rainy':0.5,'Sunny':0.5},
    'Sunny|Rainy' : {'Rainy':0.6,'Sunny':0.4},
    'Sunny|Sunny' : {'Rainy':0.3,'Sunny':0.7},
}
emission_probability = {
    'Rainy' : {'walk':0.1,'shop':0.4,'clean':0.5},
    'Sunny' : {'walk':0.6,'shop':0.3,'clean':0.1},
}
def forward_viterbi(obs,states,start_p,trans_p,emit_p):
    T = {}
    for state1 in states:
        for state2 in states:
            T[state1+"|"+state2] = (start_p[state1+"|"+state2],[state2],start_p[state1+"|"+state2])
    for output in obs:
        U = {}
        print "---------------------------------\nObservation:",output
        total = 0
        argmax = None
        valmax = 0
        print "Next state:" + next_state
        for curr_state in states:
            for prv_state in states:
                print "\tprv_state|curr_state:",prv_state+"|"+curr_state
                try:
                    (prob,v_path,v_prob) = T[prv_state+"|"+curr_state]
                except KeyError:
                    (prob,v_path,v_prob) = T[prv_state+"|"+curr_state]=(0,None,0)
                p = emit_p[curr_state][output]*trans_p[prv_state+"|"+curr_state][next_state]
                prob *= p
                v_prob *= p
                
                
forward_viterbi(observations,states,start_probability,transition_probability,emission_probability)