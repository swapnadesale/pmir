# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class QueryInfo(models.Model):
    userid = models.ForeignKey(User)
    querytext = models.TextField()
    datetime = models.DateTimeField()
    
    def __unicode__(self):
        return self.querytext

    class Meta: 
        ordering = ['-datetime'] #新到的query排在列表的前面
    
class GoogleResultInfo(models.Model):
    query = models.ForeignKey(QueryInfo)
    rank = models.IntegerField()
    title = models.TextField()
    snippet = models.TextField()
    url = models.URLField(max_length=1000)
    #clicked = models.IntegerField()
    def __unicode__(self):
        return u"T: %s\nS: %s\nU: %s\n" % (self.title, self.snippet, self.url)
    
class BaiduResultInfo(models.Model):
    query = models.ForeignKey(QueryInfo)
    rank = models.IntegerField()
    title = models.TextField()
    snippet = models.TextField()
    url = models.URLField(max_length=1000)
    #clicked = models.IntegerField()
    def __unicode__(self):
        return u"T: %s\nS: %s\nU: %s\n" % (self.title, self.snippet, self.url)
    
class PIRResultInfo(models.Model):
    query = models.ForeignKey(QueryInfo)
    engine = models.TextField()
    pirapp = models.TextField()
    rank = models.IntegerField()
    originalrank = models.IntegerField()
    #title = models.TextField()
    #snippet = models.TextField()
    #url = models.URLField(max_length=1000)
    #clicked = models.IntegerField()
    def __unicode__(self):
        return "pir result"
    
class ClickRecordInfo(models.Model):
    userid = models.ForeignKey(User)
    query = models.ForeignKey(QueryInfo)
    engine = models.TextField()
    url = models.URLField(max_length=1000)
    rank = models.IntegerField()
    time = models.DateTimeField()
    
    class Meta: 
        ordering = ['-time'] #新到的点击排在列表的前面
    

ResultInfoTable = {"google": GoogleResultInfo, "baidu": BaiduResultInfo, "pir": PIRResultInfo}
  
'''    
class PIRResultInfo(models.Model):
    queryid = models.ForeignKey(QueryInfo)
    title = models.TextField()
    snippet = models.TextField()
    url = models.URLField()
    clicked = models.BooleanField()
'''
    
    