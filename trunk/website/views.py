# Create your views here.
# coding=utf-8

from django.template import loader, Context
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
import urllib, httplib

def index(request):
    return render_to_response("index.html")
    #return HttpResponse("hello world!")
    
def control(request):
    page = request.POST.get('page')
    if not page:
        page = "googlebaidu"
        
    query = request.POST.get('topic')
        
    return render_to_response('frame.html', {'page': page, 'topic': query})

SE_URL = {"google": "http://www.google.cn/search?", "baidu":"http://www.baidu.com/s?"}

def googleResult(request):
    query = request.GET.get('q', '')
    se_url = SE_URL["google"]
    url = se_url + "q=" + query
    #url = urllib.quote(url)
    webpage = downloadpage("http://www.google.cn/search?q=python") 
    encode = "gb2312"
    webpage = webpage.decode(encode).encode("utf8")
    
    return HttpResponse(webpage)
'''
def googleResult(request):
　　params = urllib.urlencode({'q':'apple'}) 
　　headers = {"Content-type": "application/x-www-form-urlencoded","Accept": "text/plain"}
　　 #构建headers
　　conn = httplib.HTTPConnection("www.google.cn:80") #建立http连接，记得地址不要加'http://'且要加上port
　　conn.request("POST", "www.google.cn", params, headers)
　　 #发送登陆请求
　　response = conn.getresponse() #获得回复
　　print response.status, response.reason #获得请求状态
　　data = response.read() #获得登陆后的网页内容
　　conn.close() #关闭连接
'''
    

def baiduResult(request):
    query = request.GET.get('q', '')
    print query
    query = urllib.quote(query)
    se_url = SE_URL["baidu"]
          
    #queryurl = urlencode([('wd', query)])
    url = se_url + "q=" + query
    print "url: ", url
    #url = urllib.quote(url)
    webpage = downloadpage("http://www.baidu.com/s?wd=apple")
    encode = "gb2312"
    webpage = webpage.decode(encode).encode("utf8")
            
    return HttpResponse(webpage)

def downloadpage(url):
    webpage = urllib.urlopen(url).read()
    #webpage = webpage.decode("gb2312").encode("utf-8")
    print webpage
    return webpage

if __name__ == '__main__':
    
    pass
    #webpage = urlopen("http://www.google.cn/search?q=apple").read()
    #print webpage
    
    