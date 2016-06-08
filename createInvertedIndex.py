'''
Author: Yamini Joshi
Description: Inverted Index Data Structure
Command Line Input: stopwordsFile=english.stop [http://jmlr.org/papers/volume5/lewis04a/a11-smart-stop-list/english.st]
                    collectionFile=cran.all.1400 [http://ir.dcs.gla.ac.uk/resources/test_collections/cran/]
                    indexFile=invertedIndex.txt [Name of File where Inverted Index should be stored]
'''

#!/usr/bin/env python

import sys #File IO
import re #Regex
from porterStemmer import PorterStemmer #PorterStemmer
from collections import defaultdict
from array import array

porter=PorterStemmer()

class CreateInvertedIndex: #the inverted index class structure

    def __init__(self):
        self.invertedIndex=defaultdict(list)    #the inverted index
        self.docs=0
        self.words=0
        self.unique_words=0
        self.postings=0
        self.unique_words_set=set()
        self.tf=defaultdict(list)
        self.summaryIndex={} 

    def getWordStems(self, line):
        '''Input: stream of text, Output: the word stems'''
        line=line.lower() #change case of line
        line=re.sub(r'[^a-z0-9 ]',' ',line) #put spaces instead of non-alphanumeric characters
        line=line.split()
        for word in line:
            self.unique_words_set.add(word) #To calculate unique words in collection
        line=[x for x in line if x not in self.stopWords]  #eliminate the stopwords
        #print line
        line=[ porter.stem(word, 0, len(word)-1) for word in line] #get word stems from porter stemmer
        #print line
        #line=set(line) #To get rid of duplicated words
        #line=list(line)
        return line

    def getStopWords(self):
        '''get stopwords from the stopwords file and store them in a hash table'''
        f=open(self.stopWordsFile, 'r')
        stopwords=[line.strip() for line in f] #List of words in stopwords file
        self.stopWords=dict.fromkeys(stopwords) #Create stopwords dictionary with stopwords as key
        f.close()

    def parseCorpus(self):
        ''' returns the id[.I], and summary[.W] of the next page in the collection '''
        line = self.corpusFile.readline()
        words = line.split()
        if len(words) == 0:
            return {}
        doc=[]
        if words[0] == '.I': #search for .I in the beginning of a line
            docId = words [1]  #The digit followed by .I is the docId
            docSummary = ""
            line = self.corpusFile.readline()
            #print line
            words = line.split()
            while words[0] != '.W': #search for .W
                line = self.corpusFile.readline()
                words = line.split()
            last_pos = self.corpusFile.tell()
            line = self.corpusFile.readline()
            words = line.split()
            #print line
            if words[0]=='.I':
                self.corpusFile.seek(last_pos)
                d={}
                d['id']=docId
                d['summary']=''
                return d
            else:
                docSummary += line
            while words[0]!='.I': #text between .W and .T is the summary of the doc
                last_pos = self.corpusFile.tell() #store value of file pointer
                line =self.corpusFile.readline()
                words = line.split()
                try:
                    if not words[0] == '.I':

                        docSummary += line #add line to doc summary
                except:
                    break
            self.corpusFile.seek(last_pos) #undo readline()                
        d={}
        d['id']=docId
        d['summary']=docSummary
        #print 'd is here:'
        #print d
        return d

    def writeInvertedIndexToFile(self):
        '''write the inverted index to the file specified as arg[3]'''
        f=open(self.invertedIndexFile, 'w')
        print >> f, '-'.join(('Total Documents Scanned',str(self.docs)))
        for term in self.invertedIndex.iterkeys():
            numDocs=len(self.invertedIndex[term])
            tfData=','.join(map(str,self.tf[term]))
            #print self.invertedIndex[term]
            postingData=';'.join(map(str,self.invertedIndex[term]))
            #print tfData,postingData
            print >> f, '|'.join((term,postingData,tfData))
            
        f.close()
        #write title index
        f=open(self.summaryFile,'w')
        for docid, summary in self.summaryIndex.iteritems():
            print >> f, '|'.join((str(docid), summary))
        f.close()
        

    def createInvertedIndex(self):
        '''creates the inverted index'''
        self.getFileParams()
        self.corpusFile=open(self.collectionFile,'r')
        self.getStopWords()
                
        
        docDict={}
        docDict=self.parseCorpus()
        #main loop creating the index
        while docDict != {}:                    
            self.docs += 1
            lines=docDict['summary']
            docLength=len(lines.split())
            self.words += len(lines.split())
            docId=(docDict['id'])
            #print 'docDict is here:'
            #print docDict
            stems=self.getWordStems(lines)
            #build the index for the current page
            stemDict={}
            for position, term in enumerate(stems):
                #print "position, term", position, term
                freq=0
                for terms in stems:
                    if term==terms:
                        freq+=1
                if term not in stemDict:
                    stemDict[term]=docId
                    self.tf[term].append('%.4f' % (freq/float(docLength)))
            self.summaryIndex[self.docs]=docDict['summary']
            #print stemDict
            #merge the current page index with the main index
            for stem, postingpage in stemDict.iteritems():
                #print 'stem, postingpage', stem, postingpage
                self.invertedIndex[stem].append(postingpage)
                #print 'self.invertedIndex[stem]', self.invertedIndex[stem]
            docDict=self.parseCorpus()

        self.writeInvertedIndexToFile()
    
    def getFileParams(self):
        '''get the parameters stopwords file, corpus file, and the output inverted index file'''
        param=sys.argv
        self.stopWordsFile=param[1]
        self.collectionFile=param[2]
        self.invertedIndexFile=param[3] #to be created
        self.summaryFile=param[4] #to be created

    def printStatistics(self):
        print 'Number of Documents =', self.docs
        print 'Number of words in collection =', self.words
        print 'Number of unique words in collection =', len(self.unique_words_set)
        self.postings = len(self.invertedIndex.keys())
        print 'Number of entries in Inverted Index =', self.postings
        postingsList = self.invertedIndex.values()
        maxPostingsLen = len(postingsList[0])
        minPostingsLen = len(postingsList[0])
        sumPostingsLen = len(postingsList[0])
        for i in range(1,len(postingsList)):
            postingsLength = len(postingsList[i])
            if postingsLength > maxPostingsLen:
                maxPostingsLen = postingsLength 
            if postingsLength < minPostingsLen:
                minPostingsLen = postingsLength
            sumPostingsLen += postingsLength
        print 'Length of shortest postings list =', minPostingsLen
        print 'Length of longest postings list =', maxPostingsLen        
        print 'Average Length of postings list =', sumPostingsLen/(float)(len(postingsList))        
    
if __name__=="__main__":
    c=CreateInvertedIndex()
    c.createInvertedIndex()
    #c.printStatistics()

