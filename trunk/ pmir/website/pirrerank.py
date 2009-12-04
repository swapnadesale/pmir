# coding=utf-8
from termfrequency import *
from pms.website.models import *
#resultsList = ["title", "snippet", "url"]
from smallseg import SEG

def psudorerank(username, engine, top, seg):
    user = User.objects.get(username=username)
    qi = QueryInfo.objects.filter(userid=user)[0]
    resultsTable = ResultInfoTable[engine]
    resultsInfo = resultsTable.objects.filter(query=qi)
    resultsList = []
        #encoding = chardet.detect(resultsInfo[0].title)["encoding"]
        #print encoding
        #print len(resultsInfo)
    for result in resultsInfo:
        title = result.title.encode("utf8")
        resultsList.append(title)
    
    termsList = []
    for result in resultsList:
        wlist = seg.cut(result)
        termsList.append(wlist)
    
    model = []
    if top > len(resultsList):
        top = len(resultsList)
    for i in range(top):
        model.extend(termsList[i])
    
    tf_model = TermFrequency(model).getTermFreq()
    
    tfs = []
    for lst in termsList:
        tfs.append(TermFrequency(lst))
    
    i = 0
    rankKey = {}
    for tf in tfs:
        rankKey[i] = similarity(tf_model, tf.getTermFreq())
        i += 1
    
    reranked_items = sorted(rankKey.items(), key=lambda d: d[1], reverse=True)
    reranked = []
    for item in reranked_items:
        reranked.append(item[0])
    
    #newrank = 1
    #for rr in reranked:
    #    title = resultsInfo[rr].title
    #    snippet = resultsInfo[rr].snippet
    #    url = resultsInfo[rr].url
    #    pi = PIRResultInfo(query=qi, engine=engine, rank=newrank, originalrank=rr, pirapp="psudoFeedback", clicked=0)
    #    pi.save()
    #    newrank += 1
            
    query = qi.querytext.encode("utf8")
    pageContent = makePageContent(resultsInfo, reranked, query, seg)
    
    return [query, pageContent]   

def userFeedbackRerank(username, engine, seg):
    user = User.objects.get(username=username)
    queryHistory = QueryInfo.objects.filter(userid=user)
    resultsTable = ResultInfoTable[engine]
    qCurrent = queryHistory[0]
    resultsNum = len(resultsTable.objects.filter(query=qCurrent))
    #print "resultsNum: ", resultsNum
    if not queryHistory:
        return "No user history"
    
    clickedResults = []
    historyLength = 1
    clickHistory = ClickRecordInfo.objects.filter(userid=user, query=qCurrent) # according to models clickHistory is ordered by [-time]
    clickSequenceLength = 1
    for click in clickHistory:
        if clickSequenceLength <=0:
            break
        clickSequenceLength -= 1
        engine = click.engine
        rank = click.rank
        
        table = ResultInfoTable[engine]
        clickedresult = table.objects.filter(query=qCurrent, rank=rank)[0]
        clickedResults.append(clickedresult);
    
    allterms = []
    for result in clickedResults:
        terms = seg.cut(result.title.encode("utf8") + result.snippet.encode("utf8"))
        allterms.extend(terms)
        
    historyModel = TermFrequency(allterms).getTermFreq()
    
    # rerank current results Set
    
    resultsInfo = resultsTable.objects.filter(query=qCurrent)
    
    tfs = []
    for resultInfo in resultsInfo:
        featureString = resultInfo.title.encode("utf8") + resultInfo.snippet.encode("utf8")
        tfs.append(TermFrequency(seg.cut(featureString)))
    
    i = 0
    rankKey = {}
    for tf in tfs:
        rankKey[i] = similarity(historyModel, tf.getTermFreq())
        i += 1
    
    reranked_items = sorted(rankKey.items(), key=lambda d: d[1], reverse=True)
    reranked = []
    for item in reranked_items:
        reranked.append(item[0])
    
    #newrank = 1
    #for rr in reranked:
    #    title = resultsInfo[rr].title
    #    snippet = resultsInfo[rr].snippet
    #    url = resultsInfo[rr].url
    #    pi = PIRResultInfo(query=qCurrent, engine=engine, rank=newrank, originalrank=rr, pirapp="userFeedback", clicked=0)
    #    pi.save()
    #    newrank += 1
        
    query = qCurrent.querytext.encode("utf8")
    pageContent = makePageContent(resultsInfo, reranked, query, seg)
    #print reranked
    return [query, pageContent]

def userFeedbackRerankLong(username, engine, seg):
    user = User.objects.get(username=username)
    queryHistory = QueryInfo.objects.filter(userid=user)
    resultsTable = ResultInfoTable[engine]
    qCurrent = queryHistory[0]
    resultsNum = len(resultsTable.objects.filter(query=qCurrent))
    #print "resultsNum: ", resultsNum
    if not queryHistory:
        return "No user history"
    table = ResultInfoTable[engine]
    clickedResults = []
    historyLength = 1
    clickHistory = ClickRecordInfo.objects.filter(userid=user) # according to models clickHistory is ordered by [-time]
    for click in clickHistory:
        query = click.query
        if queryOverlap(query.querytext.encode("utf8"), qCurrent.querytext.encode("utf8"), seg) > 0.3:
            engine = click.engine
            rank = click.rank
        
            clickedresult = table.objects.filter(query=qCurrent, rank=rank)[0]
            clickedResults.append(clickedresult);
    
    allterms = []
    for result in clickedResults:
        terms = seg.cut(result.title.encode("utf8") + result.snippet.encode("utf8"))
        allterms.extend(terms)
        
    historyModel = TermFrequency(allterms).getTermFreq()
    
    # rerank current results Set
    
    resultsInfo = resultsTable.objects.filter(query=qCurrent)
    
    tfs = []
    for resultInfo in resultsInfo:
        featureString = resultInfo.title.encode("utf8") + resultInfo.snippet.encode("utf8")
        tfs.append(TermFrequency(seg.cut(featureString)))
    
    i = 0
    rankKey = {}
    for tf in tfs:
        rankKey[i] = similarity(historyModel, tf.getTermFreq())
        i += 1
    
    reranked_items = sorted(rankKey.items(), key=lambda d: d[1], reverse=True)
    reranked = []
    for item in reranked_items:
        reranked.append(item[0])
        
    query = qCurrent.querytext.encode("utf8")
    pageContent = makePageContent(resultsInfo, reranked, query, seg)
    #print reranked
    return [query, pageContent]


def queryOverlap(q1, q2, seg):
    termList1 = seg.cut(q1)
    termList2 = seg.cut(q2)
    tfQ1 = TermFrequency(termList1).getTermFreq()
    tfQ2 = TermFrequency(termList2).getTermFreq()
    return similarity(tfQ1, tfQ2)

def makePageContent(resultInfoList, rank, query, seg):
    template = '''<table border="0" cellpadding="0" cellspacing="0"><tr><td class="f"><a onmousedown="load('11')"     href="''' # + url 
    '''" target="_blank"><font size="3">''' #+ title
    '''</font></a><br /><font size="-1">''' # + snippet
    '''<font color="#008000">''' # + url
    '''</font> - </font></td></tr></table>'''
    pageStr = ""
    i = 0
    terms = seg.cut(query)
    for rk in rank:
        title = resultInfoList[rk].title.encode("utf8")
        snippet = resultInfoList[rk].snippet.encode("utf8")
        url = resultInfoList[rk].url.encode("utf8")
        #for term in terms:
        #    term = term.encode("utf8")
        #    title = title.replace(term, '''<font color="#c60a00">''' + term + '</font>')
        #    snippet = snippet.replace(term, '''<font color="#c60a00">''' + term + '</font>')
        #print title
        #print url
        dist = rk - i
        if dist == 0:
            arrowscript = '<font size = \"2\" color = #6F00D2 bold>[-]</font>'
        elif dist > 0:
            arrowscript = '<font size = \"2\" color = red bold>[&#8593;' + str(dist) + ']</font>'
        else:
            arrowscript = '<font size = \"2\" color = green bold>[&#8595;' + str(-dist) + ']</font>'
            
        resultStr = '''<table border="0" cellpadding="0" cellspacing="0"><tr><td class="f"><a onmousedown="load(\'''' \
                    + str(i) \
                    + '''')" href="'''\
                    + url \
                    + '''" target="_blank"><font size="3">''' \
                    + arrowscript \
                    + title \
                    + '''</font></a><br /><font size="-1">''' \
                    + snippet \
                    + '''<br /><font color="#008000">''' \
                    + url \
                    + '''<br /></font></font></td></tr></table>\n'''
        pageStr += resultStr
        i += 1

    return pageStr


if __name__ == '__main__':
    #resultsList = ["我是中国人民的儿子", "你是我儿子", "中国人民万岁", "我永远是中国人民的儿子"]
    seg = SEG()
    #print 'Load dict...'
    words = "main.dic"
    seg.set(words)
    #print "Dict is OK."
    
    #print psudorerank(resultsList, 2) 
    username = "test"
    engine = request.GET.get("engine", "")
    resultsTable = ResultInfoTable[engine]
    [query, pagecontent] = userFeedbackRerank(username, resultsTable, seg)
           
    
