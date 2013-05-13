#!/usr/bin/env python

import sys
import re

class UserAgent(object):
    def __init__(self, os, os_version, browser, browser_version):
        self.os = os
        self.os_version = os_version
        self.browser = browser
        self.browser_version = browser_version
    
    def __repr__(self):
        return self.os + " " + self.os_version + " " + self.browser + " " + self.browser_version

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

class UnknownUserAgent(object):
    def __str__(self):
        return "UNKNOWN"

class LogLine(object):
    def __init__(self, line, host, remoteip, date, ua):
        self.line = line
        self.host = host
        self.remoteip = remoteip
        self.date = date
        self.ua = ua

class InvalidLogLine(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

def parse_line(line):
    pieces = line.split(" ", 7)
    if len(pieces) < 7:
        raise InvalidLogLine("Bogus log line format: " + line)
    host = pieces[0]
    remoteip = pieces[2]
    date = pieces[5][1:]
    ua = pieces[7].split('"')[0].strip()
    return LogLine(line, host, remoteip, date, ua)

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
    possible = ".".join(non_alpha.replace('_', '.').split('.')[:2])
    if possible == "": return "UNKNOWN"
    return possible

def truncate_alpha(raw):
    return re.sub(r'[a-zA-Z\-].*', '', raw)

def parse_user_agent_windows_version(ua):
    win_version_dict = {
        "95": "95",
        "98": "98",
        "XP": "XP",
        "NT": "NT4",
        "NT 4.0": "NT4",
        "NT 5.0": "2000",
        "NT 5.1": "XP",
        "NT 5.2": "XP",
        "NT 6.0": "Vista",
        "NT 6.1": "7",
        "NT 6.2": "8",
        "NT 6.3": "Blue"
    }
    win_version_index = find_end_of_token(ua, "Windows ")
    stop_point = find_next(ua, ";)", win_version_index)
    ua_win_version = ua[win_version_index:stop_point]
    return win_version_dict.get(ua_win_version, "UNKNOWN")

def parse_user_agent_mac_version(ua):
    mac_version_index = find_end_of_token(ua, "Mac OS X ")
    stop_point = find_next(ua, ');', mac_version_index)
    return clean_up_version(ua[mac_version_index:stop_point])
    
def parse_user_agent_iphone_os_version(ua):
    iphone_version_index = find_end_of_token(ua, " OS ")
    stop_point = find_next(ua, ' ', iphone_version_index)
    likely = clean_up_version(ua[iphone_version_index:stop_point])
    if (likely == ""): return "UNKNOWN"
    return likely

def parse_user_agent_os(ua):
    if "Linux" in ua: return ("Linux", "UNKNOWN")
    if "Windows" in ua: return ("Windows", parse_user_agent_windows_version(ua))
    if "Mac OS X" in ua: return ("MacOSX", parse_user_agent_mac_version(ua))
    return ("UNKNOWN", "UNKNOWN")

#not thrilled with this approach, may be fine, but meh
def parse_user_agent(ua):
    ua_map = {
        "Android" : parse_user_agent_android,
        "iPad": parse_user_agent_ipad,
        "iPhone": parse_user_agent_iphone,
        "Firefox": parse_user_agent_firefox,
        "Chrome": parse_user_agent_chrome,
        "MSIE": parse_user_agent_ie,
        "IE": parse_user_agent_ie
    }
    for (key, parser) in ua_map.items():
        if key in ua:
            return parser(ua)
    return UnknownUserAgent()

def parse_user_agent_android(ua):
    def parse_user_agent_android_version():
        android_version_index = find_end_of_token(ua, "Android ")
        stop_point = find_next(ua, ';', android_version_index)
        return clean_up_version(ua[android_version_index:stop_point])
    #android browser follows format of safari browser version
    return UserAgent("Android", parse_user_agent_android_version(),
                     "Android", parse_user_agent_safari_version(ua))

def parse_user_agent_iphone(ua):
    return parse_user_agent_ios("iPhone", ua)

def parse_user_agent_ipad(ua):
    return parse_user_agent_ios("iPad", ua)

def parse_user_agent_ios(device, ua):
    return UserAgent(device, parse_user_agent_iphone_os_version(ua),
                     "Safari", parse_user_agent_safari_version(ua))    

def parse_user_agent_safari_version(ua):
    try:
        safari_version_index = find_end_of_token(ua, "Version/")
    except ValueError:
        return "UNKNOWN"
    stop_point = find_next(ua, ' ', safari_version_index)
    return clean_up_version(ua[safari_version_index:stop_point])

def parse_user_agent_firefox(ua):
    def parse_user_agent_firefox_version():
        ff_version_index = find_end_of_token(ua, "Firefox/")
        stop_point = find_next(ua, ' ', ff_version_index)
        if stop_point == -1: stop_point = len(ua)
        return clean_up_version(ua[ff_version_index:stop_point])
    os_details = parse_user_agent_os(ua)
    return UserAgent(os_details[0], os_details[1], "Firefox", parse_user_agent_firefox_version())

def parse_user_agent_chrome(ua):
    def parse_user_agent_chrome_version():
        chr_version_index = find_end_of_token(ua, "Chrome/")
        stop_point = ua.index('.', chr_version_index)
        return ua[chr_version_index:stop_point]
    os_details = parse_user_agent_os(ua)
    return UserAgent(os_details[0], os_details[1], "Chrome", parse_user_agent_chrome_version())

#TODO: IE on the mac?  probably different function entirely
def parse_user_agent_ie(ua):
    def parse_user_agent_ie_version():
        ie_version_index = find_end_of_token(ua, "IE ")
        next_semicolon = ua.index(";", ie_version_index)
        return ua[ie_version_index:next_semicolon]
    return UserAgent("Windows", parse_user_agent_windows_version(ua),
                     "IE", parse_user_agent_ie_version())
