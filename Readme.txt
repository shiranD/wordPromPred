There are two main folders:
src
	- begin2.py
	- set
config
	- config.yml
	- sentences_22-24_wsj.txt
	- hunpos-tag
	- function
	- negation
	- regt3.model
	- srcs

additionally, there’s another output folder with a varied name

out_+random_number

	- \d+.json

begin2.py contains the source code for feature extraction to eventually create .jsons file representation for each sentence.
Sentences to extract feats from are found in sentences_22-24_wsj.txt
config.yml contains info with regard all configuration needed to begin to work.
function, negation, are word files containing the corresponding word family.
regt3.model and hunpos-tag are the trained model and the exe file respectively.
srcs is a file with the websites which function and negation words were taken from.


I used the nltk 3.0 to load the cmudict. Also for collapsing POS tags to the narrowed version it offers. I’ve decided to make a json per sentence so that I could, If needed, work on them on parallel. A touple pair was made for each field-value and by using ordered dict I controlled the order of writing to jsons.
Due to the future, past syll. info requirement and due to memory considerations I decided to hold maximum of two word data structs at every point of time during running. When I reach the next word and it’s past syll. is filled in by keeping past info. When past_word contains info of its future (from current) it is dumped.
A problem occurred when trying to analyze symbols which are not words. Therefore, a file ‘set’ contains the sorted uniq str which weren’t found in cmudict - this should be discussed in our next meeting as well.
Does prominence can be determined among ‘full’ or only between ‘full’ to ‘reduced’.

I felt that I learned to use many tools, and faced many decisions throughout it. It was fun!