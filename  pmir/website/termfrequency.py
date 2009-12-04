# coding=utf-8
from pms.settings import *
import math

def loadStopWords(filename):
    stopwords = {}
    f = open(filename)
    while 1:
        line = f.readline().strip()
        if not line:
            break
        stopwords[line] = 1
    
    f.close()
    return stopwords

class TermFrequency:
    def __init__(self, termList):
        self.termList = termList
        self.stopwords = loadStopWords(STOP_WORDS_ADDR)
        self.termFreqMap = {}
        self.__computeTermFreq()
        
    def getTermFreq(self):
        return self.termFreqMap
            
    def __computeTermFreq(self):
        for term in self.termList:
            if term in self.stopwords:
                continue
            if term in self.termFreqMap:
                self.termFreqMap[term] += 1
            else:
                self.termFreqMap[term] = 1
    
    def display(self):
        for key, value in self.termFreqMap.items():
            print key, value

def mod(tfMap):
    sum = 0.0
    for key, freq in tfMap.items():
        sum += math.pow(freq, 2)
    return math.pow(sum, 0.5)

def innerProduct(tfMap1, tfMap2):
    sum = 0.0
    for key, freq in tfMap1.items():
        if tfMap2.has_key(key):
            sum += freq * tfMap2[key]
    
    return sum
    
def similarity(tfMap1, tfMap2):
    inner = innerProduct(tfMap1, tfMap2)
    mod1 = mod(tfMap1)
    mod2 = mod(tfMap2)
    if mod1 != 0 and mod2 != 0:
        return inner / (mod1 * mod2)
    
    return 0.0
 
if __name__ == "__main__":
    
    termList1 = ["中国", "中国", "工程", "软件", "是"]
    termList2 = ["中国", ">", "工程", "软件", "是"]
    tf = TermFrequency(termList1)
    tf2 = TermFrequency(termList2)
    print tf
    #tf.__computeTermFreq()
    termFreqMap1 = tf.getTermFreq()
    termFreqMap2 = tf2.getTermFreq()
    print mod(termFreqMap1)
    print mod(termFreqMap2)
    print innerProduct(termFreqMap1, termFreqMap2)
    print similarity(termFreqMap1, termFreqMap2)    