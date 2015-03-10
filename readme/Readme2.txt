This task was composed of several subtasks:
The first, to improve oov text and to adopt internal syllable hierarchy
The second, to test it. 
The third the begin setting the infrastructure for working with swbd.next + paper (will be referred in the meeting tomorrow)

Description of my experience with the first task:

1) In order to deal with the punctuation I wrote a simple function called 'pre_process_line' to essentially remove all unnecessary punctuation or translate it to words. 
We must not forget though, that they some day punctuation might help us in defining prominence in terms of setting boundaries of a phrase (by using commas) or assigning higher prominence score to first words when at the end we encounter a question mark.
 
2) In order to recognize numbers a number_pattern variable was constructed to find matches with the following kinds of number representations:
0.0055
0
1,200
12th
80's
12-23
20s
3\/4
80'
11,141,711
The above cases's tags were replaced with the tag '*NUMBER*'. And the default word to be analyzed was 'five' (in future we should add a number to word converter but I couldn't find a good web tool to deal with all mentioned cases)


3) A relatively small list of contractions was created (extracted from the oov set). If the algorithm encounters a word which is a contraction it concatenates it to past structure word and analyzes its phonemes again in the purpose of updating info.. It immediately ends with 'continue' statement since there was no formation of a 'current word'. 
A comment: I tried adding to contractions group "'s" however it fails to know how to contract it. McGwire vs. McGwire's was the difference between cmu dict having the phoneme output produced or not. 

4) A matching pattern was applied to recognize hyphen separated words or numbers. This is the list it's currently able to recognize:
100-point
12th-worst
12.3-inch
100-year-old
ba-2
12-12-t
12-2
one-two-three
bass-2-word
It loops through each word to extract all phoneme sequences. If it finds a number it assumes its word is 'five'. This pattern, comes to rescue once the cmu dict can't produce an output. If the following case is not matched then the word field is 'name' and then it is further analyzed to extract the phoneme sequence (of 'name'). 

5) Though I'm sure there are better ways to deal with it, when I limited the word structure to tuple pairs only, I wasn't able to modify some fields in case additional information was added in the next word (like contractions) therefore, the fields that are flexible to modifications were appended as list pairs.

6) others: the wsj database was modified to present brackets. The 'function' word-file was filtered out from non-single words. The 'negation' file is composed of 'no' , 'not'. I didn't no what to add to it.  

7) The vowels were rated according to the following rating system:
first whether the were the most stressed ones (followed by '1' symbol )
1 - tense
2 - lax + r controlled
3 - second stressed (followed by '2')
4 - the least stressed vowels (followed by '0') 

Description of my experience with the second task:
I used pep8 and auto pep8 and these are cool tools. After modifying I left a copy on purpose so I could use diffmerge to see the differences it made in the code. It is very meticulous. In addition, pylint gave me more content-wise suggestions which I implemented but left some out - upgraded my code score from 7.67 to 8.18 . The pylint output is attached.

