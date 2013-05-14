#!/usr/bin/env python

from __future__ import print_function
import sys
import re

class UserAgent(object):
    def __init__(self, os, os_version, browser, browser_version):
        self.os = os
        self.os_version = os_version
        self.browser = browser
        self.browser_version = browser_version
    
    def isUnknown(self):
        return False

    def __repr__(self):
        return self.os + ' ' + self.os_version + ' ' + self.browser + ' ' + self.browser_version

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

class UnknownUserAgent(object):
    def __init__(self, rawua):
        self.rawua = rawua

    def isUnknown(self):
        return True

    def __str__(self):
        return 'UNKNOWN'

class LogLine(object):
    def __init__(self, line, host, remoteip, date, rawua, ua):
        self.line = line
        self.host = host
        self.remoteip = remoteip
        self.date = date
        self.rawua = rawua
        self.ua = ua
    
    #TODO expand this when looking at sessions
    def __str__(self):
        return str(self.ua)

class InvalidLogLine(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

## utility functions

def token_between(target, start, stoppers, default='UNKNOWN'):
    try:
        start_index = find_end_of_token(target, start)
        stop_index = find_next(target, stoppers, start_index)
        if stop_index == -1: stop_index = len(target)
        return target[start_index:stop_index]
    except ValueError:
        return default

def find_next(target, chars, start=0):
    min_result = -1
    for char in chars:
        result = target.find(char, start)
        if result >= 0 and (min_result == -1 or result < min_result):
            min_result = result
    return min_result

def find_end_of_token(content, token):
    return content.index(token) + len(token)

def clean_up_version(raw_version):
    non_alpha = truncate_alpha(raw_version)
    possible = '.'.join(non_alpha.replace('_', '.').split('.')[:2])
    if possible == '': return 'UNKNOWN'
    return possible

def truncate_alpha(raw):
    return re.sub(r'[a-zA-Z\-].*', '', raw)

## main parsing functions

def parse_line(line):
    pieces = line.split(' ', 7)
    if len(pieces) < 7:
        raise InvalidLogLine('Bogus log line format: ' + line)
    host = pieces[0]
    remoteip = pieces[2]
    date = pieces[5][1:]
    rawua = pieces[7].split('"')[0].strip()
    ua = parse_user_agent(rawua)
    return LogLine(line, host, remoteip, date, rawua, ua)

def parse_user_agent(ua):
    ua_tuples = [
        ('Googlebot-Mobile', parse_bot_agent('Googlebot-Mobile')),
        ('Googlebot', parse_bot_agent('Googlebot')),
        ('bingbot', parse_bot_agent('bingbot')),
        ('adidxbot', parse_bot_agent('adidxbot')),
        ('msnbot', parse_bot_agent('msnbot')),
        ('AdsBot-Google-Mobile', parse_bot_agent('AdsBot-Google-Mobile')),
        ('AdsBot-Google', parse_bot_agent('AdsBot-Google')),
        ('Google-Site-Verification', parse_bot_agent('Google-Site-Verification')),
        ('Baiduspider', parse_bot_agent('Baiduspider')),
        ('YandexBot', parse_bot_agent('YandexBot')),
        ('Firefox', parse_user_agent_firefox),
        ('Android', parse_user_agent_android),
        ('iPad', parse_user_agent_ipad),
        ('iPhone', parse_user_agent_iphone),
        ('Chrome', parse_user_agent_chrome),
        ('Safari', parse_user_agent_safari),
        ('Windows Phone', parse_user_agent_windows_phone),
        ('MSIE', parse_user_agent_ie),
        ('IE', parse_user_agent_ie)
    ]
    for (key, parser) in ua_tuples:
        if key in ua:
            return parser(ua)
    return UnknownUserAgent(ua)

## OS specific parsing functions

def parse_user_agent_os(ua):
    if 'Linux' in ua: return ('Linux', 'UNKNOWN')
    if 'Windows' in ua: return ('Windows', parse_user_agent_windows_version(ua))
    if 'Mac OS X' in ua: return ('MacOSX', parse_user_agent_mac_version(ua))
    return ('UNKNOWN', 'UNKNOWN')

def parse_user_agent_windows_version(ua):
    win_version_dict = {
        '95': '95',
        '98': '98',
        'XP': 'XP',
        'NT': 'NT4',
        'NT 4.0': 'NT4',
        'NT 5.0': '2000',
        'NT 5.1': 'XP',
        'NT 5.2': 'XP',
        'NT 6.0': 'Vista',
        'NT 6.1': '7',
        'NT 6.2': '8',
        'NT 6.3': 'Blue'
    }
    ua_win_version = token_between(ua, 'Windows ', ';)')
    return win_version_dict.get(ua_win_version, 'UNKNOWN')

def parse_user_agent_mac_version(ua):
    return clean_up_version(token_between(ua, 'Mac OS X ', ');'))
    
def parse_user_agent_iphone_os_version(ua):
    return clean_up_version(token_between(ua, ' OS ', ' '))

def parse_user_agent_android(ua):
    def parse_user_agent_android_version():
        return clean_up_version(token_between(ua, 'Android ', ';'))
    #android browser follows format of safari browser version
    return UserAgent('Android', parse_user_agent_android_version(),
                     'Android', parse_user_agent_safari_version(ua))

def parse_user_agent_ios(device, ua):
    return UserAgent(device, parse_user_agent_iphone_os_version(ua),
                     'Safari', parse_user_agent_safari_version(ua))

def parse_user_agent_iphone(ua):
    return parse_user_agent_ios('iPhone', ua)

def parse_user_agent_ipad(ua):
    return parse_user_agent_ios('iPad', ua)

## browser specific parsing functions

def parse_user_agent_safari_version(ua):
    return clean_up_version(token_between(ua, 'Version/', ' '))

def parse_user_agent_firefox(ua):
    def handle_mobile_firefox():
        return UserAgent('Android', 'UNKNOWN', 'FirefoxMobile', parse_user_agent_firefox_version())
    def parse_user_agent_firefox_version():
        return clean_up_version(token_between(ua, 'Firefox/', ' '))
    if 'Android' in ua: return handle_mobile_firefox()
    os_details = parse_user_agent_os(ua)
    return UserAgent(os_details[0], os_details[1], 'Firefox', parse_user_agent_firefox_version())

def parse_user_agent_chrome(ua):
    def parse_user_agent_chrome_version():
        return clean_up_version(token_between(ua, 'Chrome/', '.'))
    os_details = parse_user_agent_os(ua)
    return UserAgent(os_details[0], os_details[1], 'Chrome', parse_user_agent_chrome_version())

def parse_user_agent_safari(ua):
    os_details = parse_user_agent_os(ua)
    return UserAgent(os_details[0], os_details[1], 'Safari', parse_user_agent_safari_version(ua))

def parse_user_agent_windows_phone(ua):
    def parse_user_agent_windows_phone_version():
        return clean_up_version(token_between(ua, 'Windows Phone OS ', ';'))
    return UserAgent("WindowsPhone", parse_user_agent_windows_phone_version(),
                     "IE", parse_user_agent_ie_version(ua))

def parse_user_agent_ie_version(ua):
    return clean_up_version(token_between(ua, 'IE ', '; '))

def parse_user_agent_ie(ua):
    return UserAgent('Windows', parse_user_agent_windows_version(ua),
                     'IE', parse_user_agent_ie_version(ua))

## bot specific parsers

def parse_bot_agent(botname):
    def parse_bot_func(ua):
        version = clean_up_version(token_between(ua, botname + '/', '; )'))
        return UserAgent(botname.title(), version, botname.title(), version)
    return parse_bot_func

## debugging methods (useful when checking coverage of parsing on real-world data

def print_all_unknown():
    for line in sys.stdin:
        line = line.strip()
        parsed = parse_line(line)
        if parsed.ua.isUnknown():
            print(parsed.ua.rawua)

def print_all_partially_unknown():
    for line in sys.stdin:
        line = line.strip()
        parsed = parse_line(line)
        if 'UNKNOWN' in str(parsed):
            print(str(parsed) + ' ' + parsed.rawua)

## main method

def map_all():
    for line in sys.stdin:
        line = line.strip()
        print(str(parse_line(line)) + ' 1')

if __name__ == '__main__':
    map_all()
#    print_all_unknown()
#    print_all_partially_unknown()
