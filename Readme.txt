There are two main folders:
src
	- begin.py
config
	- config.yml
	- sentences_22-24_wsj.txt
	- hunpos-tag
	- function
	- negation
	- regt3.model
	- srcs
output
	- \d+.json

begin.py contains the source code for feature extraction to eventually create .jsons file representation for each sentence.
sentences to extract feats from are found in sentences_22-24_wsj.txt
config.yml contains info with regard all configuration needed to begin to work.
function, negation, are word files containing the corresponding word family.
regt3.model and hunpos-tag are the trained model and the exe file respectively.
srcs is a file with the websites which function and negation words were taken from.


I used the nltk 3.0 to load the cmudict. and to collapse POS tags to the narrowed version it offers. I’ve decided to make a json per sentence so that I could, If needed, work on them on parallel. I didn’t know how to dict a tuple, so I could write it to json, without using field names (which were used eventually).
Due to the future, past syll. info requirement and due to memory considerations I decided to hold maximum of 2 word data struct at every point of time drink running. When I reach the second word and on I fill in it’s past syll. and future of 1st word so then 1st word is  ready to be dumped to json file and so on.