# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from datetime import datetime
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.template import Context, RequestContext
from django import forms
from django.contrib.auth.forms import UserCreationForm
import django.contrib.auth as auth

#from util import get_city_list, get_school_list


#from util import reset_random_password

from django.core.cache import cache
                                                  
#
#用户登录
#
def user_login(request):
    if request.session.has_key("pir_username") or request.COOKIES.has_key("pir_username"):
        return HttpResponseRedirect("/website/index/")
    if request.POST:
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = auth.authenticate(username=username, password=password)
        print "user login"
        if user is not None and user.is_active:
            # Correct password, and the user is marked "active"
            auth.login(request, user)
            request.session["pir_username"] = username
            request.COOKIES["pir_username"] = username
            request.session.SESSION_EXPIRE_AT_BROWSER_CLOSE = "true"
            # Redirect to a success page.
            return HttpResponseRedirect("/website/index/")
        else:
            # Show an error page
            print "fail"
            return render_to_response("login.html", {"fail": True})
    else:
        print "not post"
        return render_to_response("login.html", {"fail": False})

#
#用户退出
#
def user_logout(request):
    if request.user.is_authenticated():
        logout(request)
        request.session.set_expiry(0)
    return HttpResponseRedirect('/login/input/')

#
#通过邮件找回忘记密码
#

def miss_password(request, username):
    context = {}
    #检查用户名
    try:
        user = User.objects.get(username__exact=username)
    #用户名不存在
    except Exception, e:
        context['username_error'] = "该邮箱还没有注册！"
    else:
        #为用户生成新的随机密码
        if reset_random_password(user):
            return error_message_page("新密码已发送至您的邮箱，请查收！", '/login/')
        else:
            return error_message_page("新密码发送失败！请输入有效的邮箱地址", '/login/')


    return HttpResponseRedirect("/login/")


#
#用户注册，active表示是否需要邮件验证：0需要，1不需要
#
def user_register(request):
    if request.method == 'POST':
        name = request.POST.get("username")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")
        if password1 == password2:
            try:
                user = User.objects.create_user(username=name, email="", password=password1)
                user.is_staff = True
                user.save()
                request.session["pir_username"] = name
                return HttpResponseRedirect("/website/index/")
            except:
                return render_to_response("register.html", {"userexist": True})
        else:
            return render_to_response("register.html", {"pwnotmatch": True})
    else:
        return render_to_response("register.html")

def loadData(request):
    f = open("D:\\CODING\\web\\pms\\login\\usernamelist")
    while 1:
        line = f.readline()
        try:
            name, password = line.strip().split("@")
        except:
            print line
        try:
            user = User.objects.create_user(username=name, email="", password=password)
            user.is_staff = True
            user.save()
        except:
            print "load error: ", name
    
    f.close()
    return HttpResponse("Load Successfully!")
        
#
#将新注册用户添加到数据库中
#
def __add_user_to_db(post, active, host):
    user = User()
    user.username = post['email_username']
    user.email = post['email_username']
    user.set_password(post['password'])
    user.first_name = post['realname']
    user.is_active = active
    user.save()

    #为user创建mail统计记录
    mail_statistic = MailStatistic()
    mail_statistic.user = user
    mail_statistic.save()

    profile = Profile()
    profile.user = user
    if active == 0:
        from Captcha.Base import randomIdentifier
        profile.activate_code = randomIdentifier()[:20]
    profile.save()

    if active == 0:
        url = profile.activate_code+str(profile.id)
        mail_content = '''
        请通过访问此链接http://%s/login/activate/%s/ 激活您的ClubHome账户。
        '''%(host,url)
        try:
            user.email_user('ClubHome账户激活', mail_content)
        except Exception, e:
            profile.delete()
            mail_statistic.delete()
            user.delete()
            return False
    return True

#
#激活用户
#
def user_activate(request, activate_code):
    #激活前先退出，防止跳入当前登录用户页面
    if request.user.is_authenticated():
       logout(request)
       request.session.set_expiry(0)
    try:
        profile = Profile.objects.get(id=activate_code[20:],\
                                            activate_code=activate_code[:20])
    except Exception, e:
        return error_message_page("激活失败", '/')
    else:
        if profile.user.is_active:
            return HttpResponseRedirect('/login/?id=%d&already=already'
                                            %(profile.user.id))
        else:
            context = {}
            club_inviters = profile.user.clubs.filter(has_deleted=False)
            context['user'] = profile.user
            if club_inviters.count() > 0:
                template = 'invited_register.html'
                context['club_inviter'] = club_inviters[0]
                return render_to_response(template, context)
            else:
                profile.user.is_active=True
                profile.user.save()
    return HttpResponseRedirect('/login/?id=%d&next=/login/change_info/'%(profile.user.id))
#
#邀请注册，注册后自动加为邀请社团的正式成员
#
def invited_register(request):
    post = request.POST.copy()

    user = User.objects.get(id=post['id'])
    user.set_password(post['password'])
    user.first_name = post['realname']
    user.is_active = True
    user.save()

    from clubhome.club.models import UserJoinClub
    for relation in UserJoinClub.objects.filter(user=user):
        relation.is_approval = True
        relation.save(True)    #True表示需要更新club人数

    invited_user_activating(user)
    #激活注册完成后登录
    login_user = authenticate(username=user.username, password=post['password'])
    login(request, login_user)

    return HttpResponseRedirect('/login/change_info/')

years = range(1900, 2010)
months = range(1, 13)
days = range(1, 32)

#
#修改个人信息
#
@login_required
def user_change_info(request):
    context = {}
    context['user'] = request.user
    context['locations'] = get_city_list()
    context['schools'] = get_school_list()

    context['years'] = years
    context['months'] = months
    context['days'] = days

    if request.POST:
        post = request.POST.copy()
        user = request.user
        host = request.META.get('HTTP_HOST','www.ziyoudu.com')

        user.first_name = post['realname']

        if 'sex' in post:
            user.profile.sex = (post['sex'] == 'M')
        else:
            user.profile.sex = None

        if post['birth_day'] == '':
            user.profile.birth_date = None
        else:
            user.profile.birth_date = datetime.strptime(post['birth_year'] + '-'
                    + post['birth_month'] + '-'
                    + post['birth_day'], "%Y-%m-%d")

        user.profile.habitat_province = post['habitat_province']
        user.profile.habitat_city = post['habitat_city']
        user.profile.hometown_province = post['hometown_province']
        user.profile.hometown_city = post['hometown_city']
        user.profile.school_province = post['school_province']
        user.profile.school = post['school']
        user.profile.school_enrollment_year = post['school_enrollment']
        user.profile.company = post['company']
        user.profile.company_enrollment_year = post['company_enrollment']

        user.profile.hobby = post['hobby']

        user.save()
        user.profile.save()

        context['do_info'] = "修改成功"

        if post['email_username'] != user.username:
            if not user.check_password(post['oldpassword']):
                context['pw_info'] = "密码不正确"
                context['do_info'] = "密码错误"
            else:
                context['change_username_info'], context['do_info'] = \
                        __change_username(user, post['email_username'], host)

        if post['password'] != '':
            context['pw_info'], context['do_info'] = __alter_password(user,
                                        post['oldpassword'], post['password'])

        context['page_owner'] = request.user
        c = RequestContext(request, context)
        return render_to_response('change_info.html', c)

    context['page_owner'] = request.user
    c = RequestContext(request, context)
    return render_to_response('change_info.html', context)
#
#修改密码
#
def __alter_password(user, old_pw, new_pw):
    if user.check_password(old_pw):
        user.set_password(new_pw)
        user.is_staff = False #重置标志位设为False
        user.save()
        return "密码修改成功", "修改成功"
    else:
        return "旧密码不正确", "密码错误"
