The project aims at implementing a fuzzy set based information retrieval model.
The program runs in 2 steps:
A. Create an inverted index data structure from a collection of files.
B. Model the Information Retrieval system using Fuzzy set and InverstedIndex and Summary files created in Step A

A.
To run the inverted index program, issue the command:
python createInvertedIndex.py english.stop cran.all.1400 invertedIndex.txt summary.txt

The command line arguments are:
1. english.stop: The stopwords file (Source: http://jmlr.org/papers/volume5/lewis04a/a11-smart-stop-list/english.st)
2. cran.all.1400: The test file corpus (Source: http://ir.dcs.gla.ac.uk/resources/test_collections/cran/)
3. invertedIndex.txt: The file to which inverted index data structure is written. Any name can be given here.
4. summary.txt: The file which will contain summary information in the form DocID|summary.

The other files in the folder:
1. Stats.txt: Stores the statistics asked in the assignment.
2. Size.txt: Compares the inverted index file to the text corpus in terms of size. It also stores the time taken to create the invertedIndex file.

B.
To query the system, issue the command:
python queryIndex.py english.stop invertedIndex.txt summary.txt

The command line arguments are:
1. english.stop: The stopwords file (Source: http://jmlr.org/papers/volume5/lewis04a/a11-smart-stop-list/english.st)
2. invertedIndex.txt: The file to which inverted index data structure is written. This file is created in step A.
3. summary.txt: The file which contains summary information. This file was laso created in Step A.

The prompt will ask the user to enter a query
Accepted Query Form:
NonAlphabetic Letters Allowed: & | ~ which correspond to their logical counterparts.
Other non alphabetic chars are not allowed
Query could be of form: A & (B | ~C) where A,B,C are text expressions without spaces.

Infix to postfix Conversion Assumptions:
&(And) has precedence over | (Or)

Future Work:
1. Add line numbers along with the document id to give the position of the word in the document.
Problem: Only an approx position can be added based on the index of the stemmed word in the stemList created by the getWordStem function.

2. Enter multiple queries in one session.
Implemetation: Add a while loop to query function so that the prompts asks to enter more queries before exiting the program.

3. Identify Mal-formed queries.
Implementation: Postfix evaluation function can be modified to flash an error if the query is malformed.
Example: B ~C is malformed since ~ is unary, an operator is missing between B and ~C.

References:
1.http://nlp.stanford.edu/IR-book/html/htmledition/a-first-take-at-building-an-inverted-index-1.html


Author: Yamini Joshi
Contact: yamini.1691@gmail.com
