There are two main folders:
src
	- begin2.py
	- oov_set
config
	- config.yml
	- sentences_22-24_wsj.txt
	- hunpos-tag
	- function
	- negation
	- regt3.model
	- srcs

additionally, there’s another output folder with a varied name

out_+random_number{5}

	- \d+.json

begin2.py contains the source code for feature extraction to eventually create .json file representation for each sentence.
Sentences to extract feats from are found in sentences_22-24_wsj.txt
Config.yml contains info with regard to all required configurations applied to begin2.py.
Function and negation, are word files containing the corresponding word family.
Regt3.model and hunpos-tag are the trained model and the exe file respectively.
Srcs is a file with the websites sources for function and negation word files.

Decisions:
1) CMUDICT:
I used the nltk 3.0 to load the cmudict. Accessible and easy to use however, there’s an  oov problem with regard to strs that aren’t found there. *We should discuss to approach that. A file ‘oov_set’ contains the sorted uniq strs which weren’t found in cmudict.

2) COLLAPE_TAGGER:
It was used for collapsing POS tags to the 11 common tags it offers. An issue to be discussed is with regard to the sentence database. This time wsj was used and the function recognizes this source(knows what to do is wsj pos tags are given) however, what if it’s a different one.

3) OUTPUT_FILE:
I’ve decided to make a json per sentence so that I could, If needed, work on them in parallel or produce them that way. In addition config.yml is copied to each output folder to document configs. Every output folder name is generated with a random number not to override past runnings.

4) TUOPLE: 
A touple pair was made for each field-value and by using ordered dict I controlled the writing order to jsons.

5) DATA STURCT STRATEGY:
- Due to the ‘future’ and ‘past’ syll. info requirement and due to memory considerations I decided to hold maximum of two word data structs at every point of time during running.
 
- When I reach the next word and it’s ‘past’ syll. is filled in by keeping past info. and the ‘future’ of past word is fill in with its current. When past_word contains info of its ‘future’ (from current) it is dumped.

Another question: Does prominence can be determined among ‘full’ or only between ‘full’ to ‘reduced’.

I felt that I learned to use many tools, and faced many decisions throughout it. It was fun!