This task, required me to first, preprocess the SWBD data base and then compose it to feature extraction 'begin.py' we already worked on. 
First I wanted to extract the basic information needed for 'begin.py' code. This operation is done by 'nxt.py'. 

'nxt.py'
This code was mainly created for extracting core attributes of words. Words, are described in 'terminals' and 'phonewords'. Sometimes, each can be a sub group of the other, however to be aligend with the suggested hirarchy termianls.xml file contains pointers to phonwords.xml. The word, pos, timings, swbd id were extracted from terminal while the following were taken from phonewords: subword, syll stresse profile, num of sylls. Since we would like to use 'begin.py' and we wish to simulate a situation in which there will be OOV, I decided to extract the word's syllables from CMU-dict instead of using the actual words found in SWBD.
* when a subword was a bigger term than the actual word (which was most of the cases the objects was united to one regarding all its fields.

A time complexity problem I encounted was regarded to reopening of phonwords.xml every time a terminal referred to it. This process consumed time since the file was read from its begining every time a new terminal was sent. It was big Oh -  O(# of terminal words * length of phonword file (until it detects the matching reference)). Therefore, a location variable was saved as a self variable that keeps track where it last stopped (it last stopped by a 'break' statement - indicating it found a match). Every time phonwords fuction is opend it reads only a constant number of lines from the saved phonwords tree. 
This helped monitoring the matching performance. The problem that this modification created was setting the right window in order to always be within the group containing the searched query (terminal - in our case) for matching.

Tracers were implemented in additional terminal attributes: dialAct and kontrast as well as in phrases and accents which are part of phonwords.

Disfluency, describing the parts disturbing natural conversation, helped get rid of unwanted terminals. When the function initially is called it sets a dict with all termianls it refers and their appropriate attribute as a value; whether they are reperandum or repair. Since disfluency is in a form of a tree with varying number of children I made sure that only the repair type of children were considered as repair while if a repair child had an some ancestor of reperandum it was regarded as reperundum.

Another problem was, to be able to extract all middle references while given the begining reference and the end. The function 'scrollit' explicitly lists all values that the reference points to.

'begin_swbd.py'

A problem I encountered was at the process of reading json files. Every time an EOF symbol occured it messed up the chunk that was read. The file was read entirely in an iterative fashion. Later, was concatenated to one string representing all file. Then, it was seperated by '}{' suggesting the end of an object. Then, if an object contained an EOF symbol the ast.literal_eval had a problem turning the string object to a dict therefore, it got stuck. Usually, the string whould be composed of other 'left over' chunk of another string (-the first string in file that already was parsed) and contained more than one '{' character. That helped me ignore these cases (that occured no more than one time a file and 12 times total over all 150 files) and enabled the code keep parsing the rest of the objects with the current cost of missing one terminal object. 
