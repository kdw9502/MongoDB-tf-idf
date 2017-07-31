import datetime
import time
import sys
import MeCab
from pymongo import MongoClient
import math
def printMenu():
    print "1. WordCount"
    print "2. TF-IDF"
    print "3. Similarity"
    print "4. MorpAnalysis"
    print "5. CopyData"

def WordCount(docs,col_tfidf):
    print "WordCount"
    
    obj_id=raw_input("After MorpAnalysis, Input Object ID to start WordCount: ")
    for doc in docs:
        countList={}
        MorpList=doc['morp']
        for Morp in MorpList:
            countList[Morp]=countList.get(Morp,0)+1 #make WordCountList
        contentDic={}
        for key in doc.keys():
            contentDic[key]=doc[key]
        contentDic['WordCount'] =countList #add WordCount 
        col_tfidf.update({'_id':contentDic['_id']},contentDic,True)
    print "WordCount success"
#----print WordCount of input id
    docs= col_tfidf.find() 
    for doc in docs:
        if(obj_id== str(doc['_id']) ):
            for i in doc['WordCount']:
                print "%s : %d"%(i,doc['WordCount'][i])
            return 0;
            
    print "There is no Object ID %s"%(obj_id)
    return -1
    
def TfIdf(docs,col_tfidf):
    print "TF-IDF"
    obj_id=raw_input("After WordCount,Input Object ID to start TF-IDF: ")
#----------------------find idf-----
    docslen=0
    idf_divider={}
    idf={}
    for doc in docs:
        docslen+=1
        for key in doc['WordCount']:
            idf_divider[key]=idf_divider.get(key,0)+1
    for key in idf_divider:
        idf[key]=math.log(float(docslen)/idf_divider[key])
#------------------------------find tf and tf-idf and save in db
    docs=col_tfidf.find()
    for doc in docs:
        countList=doc['WordCount'] 
        tfidfList={}
        countSum=sum(countList.values())
        for key,Count in countList.items():
            tf=float(Count)/countSum
            tfidfList[key]=tf*idf[key]
        contentDic={}
        for key in doc.keys():
            contentDic[key]=doc[key]
        contentDic['TF-IDF'] =tfidfList
        col_tfidf.update({'_id':contentDic['_id']},contentDic,True)

#-------------print------------------
    docs= col_tfidf.find() 
    for doc in docs:
        if(obj_id== str(doc['_id']) ):
            count=0
            sorted_tfidf=sorted(doc['TF-IDF'].items(),key=lambda t:t[1],reverse=True)
            count=0
            for i in sorted_tfidf:
                if(count<10):
                    print "%s : %.12f"%(i[0],i[1]);count+=1
                else:
                    break
            return 0;
    print "There is no Object ID %s"%(obj_id)
    return -1

def Similarity(docs,col_tfidf):
    print "Similarity"
    
    id_1=raw_input("After TF-IDF,Input First ObjectID :")
    id_2=raw_input("Input Second ObjectID to start calculate Similarity:")
    for doc in docs:
        if(id_1==str(doc['_id'])):
            tfidf_1=doc['TF-IDF']
        if(id_2==str(doc['_id'])):
            tfidf_2=doc['TF-IDF']
#----------------make list
    for t in tfidf_1:
        if t not in tfidf_2 :
            tfidf_2[t]=0.0

    for t in tfidf_2:
        if t not in tfidf_1 :
            tfidf_1[t]=0.0
#----------------calculate
    ab=0.0
    a=0.0
    b=0.0
    for t in tfidf_1:
        ab+=tfidf_1[t]*tfidf_2[t]
        a+=tfidf_1[t]**2
        b+=tfidf_2[t]**2
    a=math.sqrt(a)
    b=math.sqrt(b)
    similarity=ab/(a*b)
    print "Similarity is %f"%(similarity)
        


def MorpAnalysis(docs,col_tfidf):
    print "MorpAnalysis"
    t=MeCab.Tagger('-d/usr/local/lib/mecab/dic/mecab-ko-dic')
    stop_word={}
    f=open("wordList.txt",'r')
    while True:
        line = f.readline()
        if not line:break
        stop_word[line.strip('\n')]=line.strip('\n')
    f.close()
    
    obj_id=raw_input("Input Object ID to start MorpAnalysis: ")
    for doc in docs:

        content=doc['content']
        nodes = t.parseToNode(content.encode('utf-8'))
        MorpList=[]
        while nodes:
            if nodes.feature[0]== 'N' and nodes.feature[1]=='N':
                w= nodes.surface
                if not w in stop_word:
                    MorpList.append(w)
            nodes = nodes.next
        contentDic={}
        for key in doc.keys():
            contentDic[key]=doc[key]
        contentDic['morp'] =MorpList
        col_tfidf.update({'_id':contentDic['_id']},contentDic,True)
    print "MorpAnalysis success"
    docs= col_tfidf.find() 
    for doc in docs:
        if(obj_id== str(doc['_id']) ):
            for i in doc['morp']:
                print(i)
            return 0;
    print "There is no Object ID %s"%(obj_id)
    return -1

def CopyData(docs,col_tfidf):
    col_tfidf.drop()
    for doc in docs:
        contentDic={}
        for key in doc.keys():
            if key!="_id":
                contentDic[key]=doc[key]
        col_tfidf.insert(contentDic)

conn=MongoClient('localhost')
db=conn['db20141494']
db.authenticate('db20141494','db20141494')
col= db['news']
col_tfidf=db['news_tfidf']

printMenu()
selector=input()

docs=col_tfidf.find()
if selector==1:
    WordCount(docs,col_tfidf);
elif selector==2:
    TfIdf(docs,col_tfidf);
elif selector==3:
    Similarity(docs,col_tfidf);
elif selector==4:
    MorpAnalysis(docs,col_tfidf);
elif selector==5:
    docs=col.find()
    CopyData(docs,col_tfidf)
