# -*- coding: utf-8 -*-
from django.db import connection
from django.contrib.auth.models import User
from clubhome.login.models import Profile
from clubhome.club.models import *
from django.core.cache import cache
#
#获取城市名列表
#
def get_city_list():
    locals = cache.get("get_city_list")
    if locals is None:
        dbh = connection
        curs = dbh.cursor()
        curs.execute('set names "utf8"')

        locals = []
        query = "SELECT cid,name FROM clubhome_city WHERE pid=0"
        curs.execute(query)
        provinces = curs.fetchall()

        for province in provinces:
            local={'province':province[1],}

            sub_query="SELECT name FROM clubhome_city WHERE pid=%s"%(province[0])
            curs.execute(sub_query)
            local['cities'] = curs.fetchall()
            locals.append(local)
        cache.set("get_city_list", locals)
        #print "not cached!"
    #else:
        #print "cached!"
    return locals
#
#获取学校列表
#
def get_school_list():
    schools = cache.get("get_school_list")
    if schools is None:
        dbh = connection
        curs = dbh.cursor()
        curs.execute('set names "utf8"')

        schools = []
        query = "SELECT cid FROM clubhome_city WHERE pid=0"
        curs.execute(query)
        provinces = curs.fetchall()

        for province in provinces:
            sub_query="SELECT name FROM clubhome_school WHERE pid=%s"%(province[0])
            curs.execute(sub_query)

            school_list = curs.fetchall()
            schools.append(school_list)
        cache.set("get_school_list", schools)

    return schools
#
#激活用户
#
def activate_user(user):
    ret = False
    if not user.is_active:
        user.is_active=True
        user.save()
        iusers = InvitedMembers.objects.filter(invitee_email=user.email)
        if iusers.count() > 0:
            iuser = iusers[0]
            iuser.status = 1 # 修改激活标志位
            iuser.save()
            ret = True
    return ret

#
#重置密码
#
def reset_random_password(user):
    import types
    if isinstance(user, (types.UnicodeType, types.StringType)):
        user = User.objects.get(id=user)
        
    #为用户生成新的随机密码
    from Captcha.Base import randomIdentifier
    new_password = randomIdentifier()[:10]

    #将随机密码发送到用户邮箱
    try:
        user.email_user('您的新密码', new_password)
        user.is_staff = True #标志位，表示密码已被重置
    except Exception, e:
        return False
    else:
        user.set_password(new_password)
        user.save()
        return True
    
