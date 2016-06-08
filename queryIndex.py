'''
Author: Yamini Joshi
'''

#!/usr/bin/env python

import sys
import re
from porterStemmer import PorterStemmer
import copy
from infixtopostfix import Stack, infixToPostfix
from collections import defaultdict
import time

porter=PorterStemmer()

class QueryIndex:

    def __init__(self):
        self.index={}
        self.tf={}
        self.numDocs=0
        self.summaryIndex=defaultdict(list)
        #self.summaryIndex=defaultdict(str)
        self.start_time=time.time()
    
    def getWordStems(self, line):
        '''Input: stream of text, Output: the word stems'''
        line=line.lower() #change case of line
        line=re.sub(r'[^a-z0-9 ]',' ',line) #put spaces instead of non-alphanumeric characters
        line=line.split()
        #for word in line:
            #self.unique_words_set.add(word) #To calculate unique words in collection
        line=[x for x in line if x not in self.stopWords]  #eliminate the stopwords
        line=[ porter.stem(word, 0, len(word)-1) for word in line] #get word stems from porter stemmer
        line=set(line) #To get rid of duplicated words
        line=list(line)
        return line

    def getStopWords(self):
        '''get stopwords from the stopwords file and store them in a hash table'''
        f=open(self.stopWordsFile, 'r')
        stopwords=[line.strip() for line in f] #List of words in stopwords file
        self.stopWords=dict.fromkeys(stopwords) #Create stopwords dictionary with stopwords as key
        f.close()
        

    def readIndex(self):
        f=open(self.indexFile, 'r');
        line = f.readline()
        string, totalDocs= line.split('-')
        self.numDocs=totalDocs
        for line in f:
            line=line.rstrip()
            term, postings, freq = line.split('|')    #term='termID', postings='docID1:pos1,pos2;docID2:pos1,pos2'
            #term, freq = header.split(':')
            freq = freq.split(',')
            #print freq
            postings=postings.split(';')        #postings=['docId1:pos1,pos2','docID2:pos1,pos2']
            #postings=[x.split('-') for x in postings] #postings=[['docId1', 'pos1,pos2'], ['docID2', 'pos1,pos2']]
            #postings=[ [int(x[0]), map(int, x[1].split(','))] for x in postings ]   #final postings list  
            self.index[term]=postings
            self.tf[term]=freq
        f.close()
        
        f=open(self.summaryFile, 'r')
        for line in f:
            if '|' in line:
                docId, summary = line.split('|')
                self.summaryIndex[docId].append(summary)
            else:
                self.summaryIndex[docId].append(line)
        f.close()
        #print self.summaryIndex

    def query(self,q):
        '''Phrase Query'''
        queryString=q
        originalQuery=q.split()
        q=self.getWordStems(q)
        #print 'q =',q
        if len(q)==0:
            print ''
            return
        #phraseDocs=self.pqDocs(q)
        for term in q:
            if term not in self.index:
                #if a term doesn't appear in the index
                #there can't be any document maching it
                return [] #Query out of scope 

        queryTerm = {}
        for term in originalQuery:
            if term not in ['&','|','~','(',')']:
                if term not in self.stopWords:
                    stem = porter.stem(term, 0, len(term)-1)
                    print 'stem =',stem
                    #vars()[term] = self.index[stem]
                    #print eval(term)
                    queryTerm[term]=(self.index[stem],self.tf[term])
                    #queryTerm.update({term: (self.index[stem],self.tf[term])})
                else:
                    #vars()[term]= []
                    queryTerm[term] = ([],[])

        #print ' '.join(map(str, phraseDocs))    #prints empty line if no matching docs
        #print eval(queryString)
        postfixQuery=infixToPostfix(queryString)
        print postfixQuery
        result = self.postfixEval(postfixQuery,queryTerm)
        self.rankDocuments(result)
        
    def getParams(self):
        param=sys.argv
        self.stopWordsFile=param[1]
        self.indexFile=param[2]
        self.summaryFile=param[3]

    def queryIndex(self):
        self.getParams()
        self.readIndex()  
        self.getStopWords() 
        print "Enter query: "
        q=sys.stdin.readline()
        self.start_time = time.time()
        self.query(q)

    def postfixEval(self, postfixExpr, queryTerm):
        operandStack = Stack()
        tokenList = postfixExpr.split()

        for token in tokenList:
            if token not in ['~','&','|','(',')']:
                #operandStack.push(token)
                tokenVal=queryTerm[token]
                operandStack.push(tokenVal)
                #print tokenVal

            elif token == '~':
                operand = operandStack.pop() 
                result = self.evaluate(token,operand)
                operandStack.push(result)
       
            else:
                operand2 = operandStack.pop()
                operand1 = operandStack.pop()
                result = self.evaluate(token,operand1,operand2)
                operandStack.push(result)
        return operandStack.pop()

    def evaluate(self, op, op1, op2=None):
        if op == "~":
            result=([],[])
            for i in range (int(self.numDocs)):
                result[0].append(str(i))
                if str(i) not in op1[0]:
                    result[1].append(1.0)
                else:
                    tf_index=op1[0].index(str(i))
                    rsv = float(op1[1][tf_index])
                    result[1].append(1-rsv)
            return result

                    
        elif op == "&":
            result=([],[])
            #print 'op1',op1
            #print 'op2',op2
            for i in range(len(op1[0])):
                #print i
                doc = op1[0][i]
                tf = op1[1][i]
                if doc in op2[0]:
                  tf2_index=op2[0].index(doc)
                  tf2=op2[1][tf2_index]
                  result[0].append(doc)
                  result[1].append(min(float(tf),float(tf2)))
                  
            #print 'result =',result
            return result

        else:
            result=([],[])
            #print 'op1',op1
            #print 'op2',op2
            for i in range(len(op1[0])):
                #print i
                doc = op1[0][i]
                tf = op1[1][i]
                if doc in op2[0]:
                  tf2_index=op2[0].index(doc)
                  tf2=op2[1][tf2_index]
                  result[0].append(doc)
                  result[1].append(max(float(tf),float(tf2)))
                else:
                  result[0].append(doc)
                  result[1].append(float(tf))
                    
            #print 'result =',result
            return result

    def rankDocuments(self, queryResult):
        #print queryResult
        print 'Fetched', len(queryResult[1]),' query results in'
        print ("--- %s seconds ---" % (time.time() - self.start_time)) 
        sortedRSV=sorted(range(len(queryResult[1])), key=lambda i:queryResult[0][i])
        sortedRSV.reverse
        if len(sortedRSV)>20:
            sortedRSV = sortedRSV[:20]
        for index in sortedRSV:
             docId=queryResult[0][index]
             print '.I', docId
             print 'RSV :',queryResult[1][index]
             #print '.W', self.summaryIndex[docId]
             print '.W', ''.join(self.summaryIndex[docId])
            

        
if __name__=="__main__":
    q=QueryIndex()
    q.queryIndex()
