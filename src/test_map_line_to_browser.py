#!/usr/bin/env python2

import unittest

from map_line_to_browser import *

class TestMapLineToBrowser(unittest.TestCase):
    def test_logline_object(self):
        res = UserAgent("osname", "osversion", "browsername", "version")
        self.assertEqual("osname osversion browsername version", str(res))

    def test_parse_line_simple_line(self):
        rawline = """www.myfavoritesite.com 192.168.20.15 212.85.128.191 - - [15/Apr/2013:00:16:07 -0400] AdsBot-Google-Mobile (+http://www.google.com/mobile/adsbot.html) Mozilla (iPhone; U; CPU iPhone OS 3 0 like Mac OS X) AppleWebKit (KHTML, like Gecko) Mobile Safari "GET /favorie/page.html HTTP/1.1" 200 5604"""
        res = parse_line(rawline)
        self.assertEqual("www.myfavoritesite.com", res.host)
        self.assertEqual("212.85.128.191", res.remoteip)
        self.assertEqual("15/Apr/2013:00:16:07", res.date)
        self.assertIsNotNone(res.ua)

    def test_parse_line_error(self):
        rawline = "Error writing to log file.     538567 messages lost."
        res = parse_line(rawline)
        self.assertEqual(rawline, res.line)

    def test_parse_line_short_line(self):
        rawline = "Short"
        with self.assertRaises(InvalidLogLine) as exc:
            parse_line(rawline)
        self.assertIn("Short", exc.exception.value)

    def test_parse_user_agent(self):
        for (expected, rawua) in self.get_all_user_agent_cases().items():
            self.assertEquals(expected, parse_user_agent(rawua))

    @staticmethod
    def get_all_user_agent_cases():
        return {
            UserAgent("Windows", "7", "IE", "7.0") :
              "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/4.0; GTB7.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C)",
            UserAgent("Windows", "Blue", "IE", "11.0") :
              "Mozilla/5.0 (IE 11.0; Windows NT 6.3; Trident/7.0; .NET4.0E; .NET4.0C; rv:11.0) like Gecko",
            UserAgent("Windows", "Vista", "IE", "8.0") :
              "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)",
            UserAgent("Windows", "XP", "IE", "7.0") :
              "Mozilla/5.0 (Windows; U; MSIE 7.0; Windows NT 5.2)",
            UserAgent("Windows", "XP", "IE", "7.0") :
              "Mozilla/5.0 (Windows; U; MSIE 7.0b; Windows NT 5.2)",
            UserAgent("Windows", "UNKNOWN", "IE", "9.0") :
              "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 7.1; Trident/5.0)",
            UserAgent("Linux", "UNKNOWN", "Chrome", "26") :
              "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.63 Safari/537.31",
            UserAgent("Windows", "XP", "Chrome", "11") :
              "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/534.21 (KHTML, like Gecko) Chrome/11.0.682.0 Safari/534.21",
            UserAgent("MacOSX", "10.8", "Chrome", "26") :
              "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_3) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.43 Safari/537.31",
            UserAgent("Windows", "7", "Firefox", "4.0") :
              "Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
            UserAgent("Windows", "7", "Firefox", "23.0") :
              "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:23.0) Gecko/20131011 Firefox/23.0",
            UserAgent("MacOSX", "10.6", "Firefox", "4.0") :
              "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0b8) Gecko/20100101 Firefox/4.0b8",
            UserAgent("Windows", "XP", "Firefox", "3.6") :
              "Mozilla/5.0 (Windows; U; Windows NT 5.1; fr; rv:1.9.2b4) Gecko/20091124 Firefox/3.6 (.NET CLR 3.5.30729)",
            UserAgent("iPad", "3.2", "Safari", "4.0") :
              "Mozilla/5.0(iPad; U; CPU iPhone OS 3_2 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Version/4.0.4 Mobile/7B314 Safari/531.21.10",
            UserAgent("iPad", "5.0", "Safari", "5.1") :
              "Mozilla/5.0 (iPad; CPU OS 5_0 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9A334 Safari/7534.48.3",
            UserAgent("iPhone", "5.0", "Safari", "5.1") :
              "Mozilla/5.0 (iPhone; CPU iPhone OS 5_0 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9A334 Safari/7534.48.3",
            UserAgent("iPhone", "UNKNOWN", "Safari", "3.0") :
              "Mozilla/5.0 (iPhone; U; CPU like Mac OS X; en) AppleWebKit/420+ (KHTML, like Gecko) Version/3.0 Mobile/1A543a Safari/419.3",
            UserAgent("Android", "0.5", "Android", "UNKNOWN") :
              "Mozilla/5.0 (Linux; U; Android 0.5; en-us) AppleWebKit/522+ (KHTML, like Gecko) Safari/419.3",
            UserAgent("Android", "2.2", "Android", "4.0") :
              "Mozilla/5.0 (Linux; U; Android 2.2; en-us; Nexus One Build/FRF91) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
            UserAgent("Android", "1.6", "Android", "3.1") :
              "Mozilla/5.0 (Linux; U; Android 1.6; en-gb; Dell Streak Build/Donut AppleWebKit/528.5+ (KHTML, like Gecko) Version/3.1.2 Mobile Safari/ 525.20.1",
            UserAgent("Android", "2.1", "Android", "4.0") :
              "Mozilla/5.0 (Linux; U; Android 2.1-update1; de-de; HTC Desire 1.19.161.5 Build/ERE27) AppleWebKit/530.17 (KHTML, like Gecko) Version/4.0 Mobile Safari/530.17",
            UserAgent("Android", "2.2", "Android", "4.0") :
              "Mozilla/5.0 (Linux; U; Android 2.2; en-us; DROID2 GLOBAL Build/S273) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
            UserAgent("Android", "2.2", "Android", "4.0") :
              "Mozilla/5.0 (Linux; U; Android 2.2; en-gb; GT-P1000 Build/FROYO) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
            UserAgent("Android", "UNKNOWN", "FirefoxMobile", "20.0") :
              "Mozilla/5.0 (Android; Mobile; rv:20.0) Gecko/20.0 Firefox/20.0",
            UserAgent("Windows", "UNKNOWN", "IE", "10.0") :
              "Mozilla/5.0 (compatible; MSIE 10.0; Win64; Trident/6.0)",
            UserAgent("MacOSX", "10.6", "Safari", "5.1") :
              "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/537.13+ (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2",
            UserAgent("Googlebot", "2.1", "Googlebot", "2.1") :
              "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
            UserAgent("Bingbot", "2.0", "Bingbot", "2.0") :
              "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)",
            UserAgent("Adidxbot", "2.0", "Adidxbot", "2.0") :
              "adidxbot/2.0 (+http://search.msn.com/msnbot.htm)",
            UserAgent("Msnbot", "2.0", "Msnbot", "2.0") :
              "msnbot/2.0b (+http://search.msn.com/msnbot.htm)",
            UserAgent("Adsbot-Google", "UNKNOWN", "Adsbot-Google", "UNKNOWN") :
              "AdsBot-Google (+http://www.google.com/adsbot.html)",
            UserAgent("Google-Site-Verification", "1.0", "Google-Site-Verification", "1.0") :
              "Mozilla/5.0 (compatible; Google-Site-Verification/1.0)",
            UserAgent("Baiduspider", "2.0", "Baiduspider", "2.0") :
              "Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)",
            UserAgent("Yandexbot", "3.0", "Yandexbot", "3.0") :
              "Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)"
        }
