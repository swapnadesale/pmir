# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from clubhome.club.models import Club
from django.conf import settings
from django.core.cache import cache

#
#存放IM配置相关信息
#
class IM_Config(models.Model):
    #屏蔽下行消息开关
    is_shielded = models.BooleanField(default=False)
    #限时屏蔽，屏蔽结束时间
    shield_until = models.DateTimeField(default="1900-01-01 00:00:00")
    #当前操作的社团
    cur_club = models.ForeignKey(Club, null=True)

#
#重载models.Manager，加入缓存机制
#
class ProfileManager(models.Manager):
    use_for_related_fields = True

    def get(self, *args, **kwargs):
        #get user id
        user_id = None
        for key, value in kwargs.items():
            if key == 'user__id__exact' or key == 'user__pk':
                user_id = value
                break
            
        if user_id is None:
            return models.Manager.get(self, *args, **kwargs)

        #get user from cache
        if settings.ACTIVE_CACHE:
            profile = cache.get('clubhome_profile_%d' % int(user_id))
            if profile:
                return profile

        #user is not in cache, get it from database
        obj = models.Manager.get(self, *args, **kwargs)

        #save user into cache
        if settings.ACTIVE_CACHE:
            cache.set('clubhome_profile_%d' % int(user_id), obj)
        return obj

#
#存储用户详细信息
#
class Profile(models.Model):
    user = models.OneToOneField(User)
    #性别
    sex = models.BooleanField(null=True)
    #出生日期
    birth_date = models.DateField(null=True)
    #现居住省份
    habitat_province = models.CharField(max_length=45)
    #现居住城市
    habitat_city = models.CharField(max_length=45)
    #家乡所在省份
    hometown_province = models.CharField(max_length=45)
    #家乡所在城市
    hometown_city = models.CharField(max_length=45)
    #学校所在省份
    school_province = models.CharField(max_length=45)
    #学校所在城市
    school = models.CharField(max_length=45)
    #入学年份
    school_enrollment_year = models.CharField(max_length=4)
    #公司名称
    company = models.CharField(max_length=45)
    #入职年份
    company_enrollment_year = models.CharField(max_length=4)
    #手机号
    cellphone = models.CharField(max_length=15)
    #QQ号
    qq = models.CharField(max_length=10)
    #MSN账号
    msn = models.CharField(max_length=50)
    #msn配置
    msn_config = models.ForeignKey(IM_Config, null=True)
    #头像图片路径
    logo_path = models.CharField(max_length=80)
    #激活码
    activate_code = models.CharField(max_length=20)
    #兴趣爱好
    hobby = models.CharField(max_length=100, default='')
    #是否被封杀
    is_blocked = models.BooleanField(default=False)

    objects = ProfileManager()


    def __str__(self):
        return "%s's profile" % self.user.username
    #
    #重载save函数，处理缓存
    #
    def save(self):
        if self.id:
            cache.delete('clubhome_profile_%d' % self.user_id)
        return models.Model.save(self) 
        

    class Admin:
        pass

