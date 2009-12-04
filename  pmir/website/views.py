# Create your views here.
# coding=utf-8

from django.template import loader, Context
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from pms.website.models import *
from pms.website.pirrerank import *
from django.views.decorators.cache import cache_page
import urllib, httplib, urllib2, re, datetime, time
import chardet, traceback, copy


seg = SEG()
#print 'Load dict...'
words = "main.dic"
seg.set(words)
#print "Dict is OK."

# Global Variables
ReturnNum = '30'
log = "server.log"
SE_URL = {"google": "http://www.google.cn/search?", "baidu":"http://www.baidu.com/s?"}

def errorlog(message, filename=log):
    f = open(filename, "a+")
    #t = datetime.datetime().now()
    #f.write(t + "\n")
    f.write(message + "\n")
    f.close()

def debugPrint(message):
    #print message
    pass
    
def index(request):
    # 如果已登录，到检索页面。否则，到注册页面。
    debugPrint("index")
    if request.session.has_key("pir_username"): 
        username = request.session["pir_username"]
        debugPrint('username: ' + username)
        return render_to_response("index.html", {"username": username})
    elif request.COOKIES.has_key("PIR_USERNAME"): # deal with old edition
        request.session["pir_username"] = request.COOKIES["PIR_USERNAME"]
        username = request.session["pir_username"]
        debugPrint('username: ' + username)
        return render_to_response("index.html", {"username": username})
    else:
        debugPrint("index to login")
        return HttpResponseRedirect("/login/input")
    
def control(request):
    debugPrint("control")
    if request.session.has_key("pir_username"):     
        query = request.POST.get('query').encode("utf8")
        name = request.session["pir_username"]
        #print "query: ", query
        saveQuery(query, name)
        return render_to_response('frame.html', {'query': query})
    else:
        debugPrint("index to login")
        return HttpResponseRedirect("/login/input/")

control = cache_page(control, 60 * 3)

def personal(request):
    if request.session.has_key("pir_username"):     
        username = request.session["pir_username"]
        return render_to_response('personal.html', {'username': username})
    else:
        debugPrint("index to login")
        return HttpResponseRedirect("/login/input/")


def saveQuery(query, name):
    userobj = User.objects.get(username=name)
    qi = QueryInfo(userid=userobj, querytext=query, datetime=datetime.datetime.now())
    qi.save()
    errorlog("query saved", log)
    
def inputpage(request):
    ''' this modual corresponds to the inputing part of page ./control
    '''
    name = request.session["pir_username"] 
    if request.GET:
        # GET message from frame.html
        query = request.GET.get('q', '').encode("utf8")
        #print chardet.detect(query)
        #encoding = chardet.detect(query)["encoding"]
        #print encoding
        #query = query.decode(encoding, "ignore").encode("utf8", "ignore")
        #print query
        #saveQuery(query, name)
        errorlog("render_to_response", log)
        return render_to_response("inputpage.html", {"q": query, "username": name})
    
    if request.POST: 
        # POST message from inputpage.html or inputpage_bg.html or inputpage_bp.html
        #print chardet.detect(request.POST.get('query', ''))
        query = request.POST.get('query', '').encode("utf8", "ignore")
        select1 = request.POST.get('GeneralSearch', '')
        select2 = request.POST.get('OptionalSearch', '')
        saveQuery(query, name)
        if select1 == "baidu" and select2 == "google":
            return render_to_response("inputpage.html", {"q": query, "username": name, "baidugoogle": True})
        elif select1 == "baidu":
            return render_to_response("inputpage.html", {"q": query, "username": name, "baidupir": True, "pir": select2})
        elif select1 == "google":
            return render_to_response("inputpage.html", {"q": query, "username": name, "googlepir": True, "pir": select2})

def baiduResult(request):
    ''' this modual is to extract results from baidu page and reorganize that to display in one of the frame.
        results are got by simulating browser's request
    ''' 
    start = time.clock()
    query = request.GET.get('q', '').encode("utf8", "ignore")
    #print query
    query = query.replace(" ", "+")    
    name = request.session["pir_username"]
    se_url = SE_URL["baidu"]
    query_gb = query.decode("utf8", "ignore").encode("gb2312", "ignore")
    url= se_url + "wd=" + query_gb + "&rn=" + ReturnNum
    header = {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.8.1.14) Gecko/20080404 (FoxPlus) Firefox/2.0.0.14'}
    req = urllib2.Request(url, headers = header)
    reader = urllib2.urlopen(req)
    data = reader.read()
    end = time.clock()
    #print "search time: ", end - start
    #encoding = chardet.detect(data)["encoding"]
    encoding = "gb2312"
    data = data.decode(encoding, "ignore").encode("utf8", "ignore")
    data = extractBaiduContent(data, name)
    #print request.GET
    if "pir" in request.GET:
        pirapp = request.GET.get('pir', '')
        script = '<script>parent.document.getElementById("right").contentWindow.location.href = "/website/' + pirapp + "/?engine=baidu&username=".encode("utf8") + name + "\";</script>".encode("utf8")
        data = data + script.encode("utf8");

    t = time.clock()
    #print "page time: ", t - end
    return render_to_response("baiduresult.html", {"query": query, "resultset": data, "searchtime": str(end - start)[0:5], "pageprocessing": str(t - end)[0:5]})

def extractBaiduContent(pagecontent, name): 
    # build the BeautifulSoup Object
    #soup = BeautifulSoup(pagecontent)
    
    # get the user and most recent query of her/him
    user = User.objects.get(username=name)
    qi = QueryInfo.objects.filter(userid=user)[0]
            
    num = 0 # record the rank
    tag = re.compile("<(.*?)>")      #匹配标签，采取不贪婪模式
    table_tags = re.compile('(<table border="0" cellpadding="0" cellspacing="0" id=.*?href="(.*?)".*?<font size="3">(.*?)</font></a>.*?<font size=-1>(.*?)<br><font color="#008000">.*?</table>)', re.DOTALL) 
    onmousedown_tag = re.compile('onmousedown="(.*?)"')
    tables = re.findall(table_tags, pagecontent)    
    beStored = False
    results = BaiduResultInfo.objects.filter(query=qi)
    if results:
        beStored = True
     
    resultStr = ""
    num = 1
    for table in tables:
            #try:
            tableStr = onmousedown_tag.sub("onmousedown=\"load('" + str(num) + "')\"", table[0])
            url = table[1]
            title =  tag.sub("", table[2])
            snippet =  tag.sub("", table[3])      
            if not beStored:
                baiduresult = BaiduResultInfo(query=qi, rank=num, title=title, snippet=snippet, url=url)
                baiduresult.save()
            num += 1
            resultStr += tableStr + "\n"
            #except Exception, e:
            #exstr = "baiduSaveError " + "User: " + name
            #print exstr
            #errorlog(exstr)
    resultStr = resultStr.replace("/s?", "http://www.baidu.com/s?")
    return resultStr

def googleResult(request):
    ''' this modual is to extract results from google page and reorganize that to display in one of the frame.
        results are got by simulating browser's request
    ''' 
    start = time.clock()
    query = request.GET.get('q', '').encode("utf8", "ignore")
    #print query
    user = request.session["pir_username"]
    #query = query.replace(" ", "+")
    queryencode = urllib.urlencode({"q": query, "num": ReturnNum})    
    se_url = SE_URL["google"]
    url= se_url + queryencode;
    header = {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.8.1.14) Gecko/20080404 (FoxPlus) Firefox/2.0.0.14'}
    req = urllib2.Request(url, headers = header)
    reader = urllib2.urlopen(req)
    data = reader.read()
    end = time.clock()
    #print "search time: ", end - start
    data = extractGoogleContent(data, user)
    #print request.GET
    if "pir" in request.GET:
        #print "pir"
        pirapp = request.GET.get('pir', '')
        script = '<script>parent.document.getElementById("right").contentWindow.location.href = "/website/' + pirapp + "/?engine=google&username=".encode("utf8") + user + "\";</script>".encode("utf8")
        data = data + script.encode("utf8");
    t = time.clock()
    #print "page time: ", t - end
    #return HttpResponse(data)
    query = urllib.quote(query)
    return render_to_response("googleresult.html", {"query": query, "resultset": data, "searchtime": str(end - start)[0:5], "pageprocessing": str(t - end)[0:5]})   

def extractGoogleContent(pagecontent, name):
    user = User.objects.get(username=name)
    qi = QueryInfo.objects.filter(userid=user)[0]
    
    tag = re.compile("<(.*?)>")      #匹配标签，采取不贪婪模式
    onmousedown_tag = re.compile('onmousedown="(.*?)"')
    li_tag = re.compile('(<li class=g><h3 class=r><a href="(.*?)".*?>(.*?)</a></h3>(<div class="*s"*>(.*?)<cite>.*?</div>)*)')

    ol_start = pagecontent.find("<ol>")
    ol_end = pagecontent.find("</ol>", ol_start)

    olpart = pagecontent[ol_start: ol_end + 5]
    while 1:
        ts = olpart.find('<table class=ts><tr><td class=fwtc><table class=ts>')
        te = olpart.find("</table></table>")
        if (ts != -1 and te != -1):
            olpart = olpart[0: ts] + olpart[te + len("</table></table>"):]
        else:
            break
    
    resultlist = re.findall(li_tag, olpart)

    beStored = False
    results = GoogleResultInfo.objects.filter(query=qi)
    if results:
        beStored = True
    
    resultStr = ""
    num = 1
    for result in resultlist:
        tableStr = onmousedown_tag.sub("onmousedown=\"load('" + str(num) + "')\"", result[0])
        tableStr = tableStr.replace('imgres?imgurl=', "")
        tableStr = tableStr.replace('"/search?', 'http://www.google.cn/search?')
        tableStr = tableStr.replace('"/url?q=', "")
        tableStr = tableStr.replace('"/images/', '"http://www.google.cn/imagres/')
        url = result[1]
        title =  tag.sub("", result[2])
        snippet =  tag.sub("", result[4])        
        if not beStored:
            googleresult = GoogleResultInfo(query=qi, rank=num, title=title, snippet=snippet, url=url)
            googleresult.save()
        num += 1
        resultStr += tableStr + "\n"
        
    return resultStr
 
def clickrecord(request):
    rank = request.GET.get('rank')
    site = request.GET.get('site')
    name = request.session["pir_username"]
    #print "rank: ", rank
    #print "site: ", site
    #print "username: ", name
    table = ResultInfoTable[site]
    user = User.objects.get(username=name)
    qi = QueryInfo.objects.filter(userid=user)[0]
    try:
        result = table.objects.filter(query=qi, rank=rank)[0]
        url = result.url
        time = datetime.datetime.now()
        ci = ClickRecordInfo(userid=user, query=qi, engine=site, rank=rank, url=url, time=time)
        ci.save()
    except:
        pass
    return render_to_response("click.html")

def psudoFeedback(request):
    #print "psudoFeedback"
    start = time.clock()
    username = request.session["pir_username"]
    engine = request.GET.get("engine", "")
    
    [query, pageContent] = psudorerank(username, engine, 3, seg)
    end = time.clock()
    return render_to_response("pirresult.html", {"query": query, "resultset": pageContent, "time": str(end - start)[0:5]})

def userFeedback(request):
    #print "userFeedback"
    start = time.clock()
    username = request.session["pir_username"]
    engine = request.GET.get("engine", "")
    resultsTable = ResultInfoTable[engine]
    [query, pageContent] = userFeedbackRerankLong(username, engine, seg)
    end = time.clock()
    return render_to_response("pirresult.html", {"query": query, "resultset": pageContent, "time": str(end - start)[0:5]})

if __name__ == '__main__':
    
    pass

    
    