This task, required me to first, preprocess the SWBD data base and the compose it to feature extraction 'begin.py' we already worked on. 
First I wanted to extract the basic information needed for 'begin.py' code. 

'nxt.py'
This code was mainly created for extracting core attributes of words. Words, are described in 'terminals' and 'phonewords'. Sometimes, each can be a sub group of the other, however to be aligend with the suggested hirarchy termianls.xml file contains pointers to phonwords.xml. The word, pos, timings, swbd id were extracted from terminal while the following were taken from phonewords: subword, syll stresse profile, num of sylls. Since we would like to use 'begin.py' and we wish to simulate a situation in which there will be OOV, I decided to extract the word's syllables from CMU-dict instead of using the actual words found in SWBD.

A time complexity problem I encounted was regarded to reopening of phonwords.xml every time a terminal referred to it. This process consumed time since the file was read from fisrt line every time a new terminal was sent. It was big Oh -  O(# of terminal words * length of phonword file (until it detects the matching reference)). Therefore, a location variable was saved as a self variable that keeps track where it last stopped (it last stopped by a 'break' statement - indicating it found a match). Every time phonwords fuction is opend it reads only a constant number of lines from the saved phonwords tree. 
This helped monitoring the matching performance. The problem that this modification created was setting the right window in order to always be within the group containing the searched query (terminal - in our case) for matching.

Tracers were implemented in additional terminal attributes: dialAct, disfluency, syntax and kontrast as well as in phrases which are part of phonwords

Another problem was, to be able to extract all middle references while given the begining reference and the end. The function 'scrollit' explicitly lists all values that the reference points to.

