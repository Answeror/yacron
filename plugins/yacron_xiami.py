import crython
import re
from http.cookiejar import CookieJar
from urllib.request import build_opener, Request, HTTPCookieProcessor
from urllib.parse import urlencode
import logging


uid_re = '/web/friends/id/([0-9]*)"'
log = logging.getLogger('yacron.xiami')


# change following lines
email = 'answeror@gmail.com'
password = '42'


def make_opener():
    cookie = CookieJar()
    return build_opener(HTTPCookieProcessor(cookie))


def login(opener):
    login_url = 'http://www.xiami.com/web/login'
    login_data = urlencode({
        'email': email,
        'password': password,
        'LoginButton': '登录',
        'remember': 1,
    }).encode('utf-8')
    login_headers = {
        'Referer': 'http://www.xiami.com/web/login',
        'User-Agent': 'Opera/9.60'
    }
    login_request = Request(login_url, login_data, login_headers)
    opener.open(login_request)
    profile_url = 'http://www.xiami.com/web/profile'
    profile_request = Request(profile_url, headers=login_headers)
    profile_response = opener.open(profile_request).read()
    ret = re.findall(uid_re, profile_response.decode('utf-8'))
    return ret[0] if ret else None


def output(resp):
    ret = parse(resp.decode('utf-8'))
    if ret:
        log.info('checkin days: %s' % ret)
    else:
        log.info('checkin response: %s' % resp)


def checkin(opener, user):
    checkin_url = 'http://www.xiami.com/web/checkin/id/' + user
    checkin_headers = {
        'Referer': 'http://www.xiami.com/web/',
        'User-Agent': 'Opera/9.99'
    }
    checkin_request = Request(checkin_url, None, checkin_headers)
    checkin_response = opener.open(checkin_request).read()
    checkin_pattern = re.compile(r'<a class="check_in" href="(.*?)">')
    checkin_result = checkin_pattern.search(checkin_response.decode('utf-8'))
    if not checkin_result:
        output(checkin_response)
    else:
        checkin_url = 'http://www.xiami.com' + checkin_result.group(1)
        checkin_headers = {
            'Referer': 'http://www.xiami.com/web',
            'User-Agent': 'BH_Toolchain0.5'
        }
        checkin_request = Request(checkin_url, None, checkin_headers)
        checkin_response = opener.open(checkin_request).read()
        output(checkin_response)


def parse(s):
    ret = re.search(r'<div class="idh">已连续签到(\d+)天</div>', s)
    return ret.group(1) if ret else None


@crython.job(expr='@hourly')
#@crython.job(second='*/10')
def run():
    '''https://github.com/isombyt/xiamiCheckin/blob/master/main.py'''
    try:
        log.info('xiami start')
        opener = make_opener()
        user = login(opener)
        if not user:
            log.info('login failed')
        else:
            checkin(opener, user)
        log.info('xiami done')
    except Exception as e:
        log.error('xiami failed')
        log.exception(e)
