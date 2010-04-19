# -*- coding: utf-8 -*-
import logging
import re
from google.appengine.api import urlfetch

from google.appengine.api import memcache


from urllib import urlencode, unquote
from BeautifulSoup import BeautifulSoup

logging.getLogger().setLevel(logging.DEBUG)


class IwiwLoginError(Exception):
   def __str__(self):
     return "nem sikerult bejelentkezni"

class NincsTalalatError(Exception):
   def __init__(self, value):
      self.value = value
   def __str__(self):
      return repr(self.value)

class Iwiw:
  def search(self, **searchparams):
    results = memcache.get(urlencode(searchparams))
    if results is not None:
      return results
    else:
      searchurl = "http://iwiw.hu/search/pages/user/ajaxsearch.jsp?do=AdvancedSearch&page=0&"
      iwiwsearch = urlfetch.fetch(searchurl + urlencode(searchparams), headers={'Cookie': self.logincookie}).content
      leves = BeautifulSoup(iwiwsearch)
      cuccok = []
      for kartya in leves.findAll("div", "cardContainer"):
        nev = kartya.findAll("a")[1].string.strip()
        name = nev.split("[")[0]
        try:
          nick = re.search("\[(?P<nick>.*)\]", nev).group(1)
        except AttributeError:
          nick = ""
        profile_url = kartya.findAll("a")[1]["href"]
        try:
           pic_popup_url = kartya.find("a", "user_image")["onclick"].split("'")[1]
        except KeyError:
          pic_popup_url = ""
        try:
          pic_thumbnail = kartya.find("a", "user_image").img["src"]
        except KeyError:
          pic_thumbnail = ""
        try:
          city = kartya.find("div", "city").string.strip()
        except AttributeError:
          city = ""
        tutu = {"name": name, "nick": nick, "profile_url": profile_url, "pic_popup_url": pic_popup_url, "pic_thumbnail": pic_thumbnail, "city": city}
      cuccok.append(tutu)
      logging.error(urlencode(searchparams))
      memcache.add(urlencode(searchparams), cuccok)
      return cuccok
  def firstn(self, count=5, **kwargs):
    url = "http://iwiw.hu/search/pages/user/ajaxsearch.jsp?do=AdvancedSearch&page=0&"
    url += urlencode(kwargs)
    iwiwsearch = urlfetch.fetch(url, headers={'Cookie': self.logincookie}).content
    #try:
    leves = BeautifulSoup(iwiwsearch)
    mennyivan = len(leves.findAll("div", "cardContainer"))
    count=int(count)
    if mennyivan - count >= 0:
      mennyit = count
    if mennyivan - count < 0:
      mennyit = mennyivan
    results = []
    for i in range(mennyit):
      ez = leves.findAll("div", "cardContainer")[i]
      # userid = ez.find("a")["name"].replace("uid","")
      ebben_van_a_popup_url = ez.findChildren("a")[2]["onclick"]
      pic_popup_url = re.search("'.*?'", ebben_van_a_popup_url).group(0)
      pic_thumbnail = ez.img["src"]
      name = ez.findChildren("a")[1].contents[0]
      profile_url = ez.findChildren("a")[1]["href"]
      result = {
          "name": name,
          "profile_url": profile_url,
          "pic_thumbnail": pic_thumbnail,
          "pic_popup_url": pic_popup_url
          }
      # result beleírása
      results.append(result)
    return results
    #except AttributeError:
    #  raise NincsTalalatError(url)
  def showfirstmatch(self, **kwargs):
    url = "http://iwiw.hu/search/pages/user/ajaxsearch.jsp?do=AdvancedSearch&page=0&"
    url += urlencode(kwargs)
    iwiwsearch = urlfetch.fetch(url, headers={'Cookie': self.logincookie}).content
    try:
      leves = BeautifulSoup(iwiwsearch)
      # userid = re.search("userID=([0-9]*)", iwiwsearch ).group(1)
      # pic_thumbnail = re.search("<img.*src=\"(.*?)\"", iwiwsearch).group(1)
      pic_popup_url = re.search("/pages/main/imageview.jsp\?.*?'", iwiwsearch).group(0).replace("&amp;", "&")
      name = leves.find("div", "cardContainer").findChild("a").findNextSibling().text 
      profile_url = leves.find("div", "cardContainer").findChild("a").findNextSibling()["href"]
      pic_thumbnail = leves.find("div", "cardContainer").img["src"]
      result = {
        "searchurl": url,
        "profile_url": profile_url,
        #"userid": userid, 
        "name": name,
        "pic_thumbnail": pic_thumbnail, 
        "pic_popup_url": pic_popup_url,
      }
      return result
    except AttributeError:
      raise NincsTalalatError(url)
  def __init__(self, email="iwiw@bergengocia.net", password="asdfasdf", logincookie="JSESSIONID=1267529305187_oxMjcxYzk0NzgxYTo3MTlk5267843077287685; Path=/, password=5ca9030fb22494a0e2866d02b3bfdfa1; Expires=Tue, 19-Oct-2010 23:01:45 GMT; Path=/, autoLoginLimited=0; Expires=Thu, 01-Jan-1970 00:00:10 GMT; Path=/, autoLoginLimited=0; Expires=Thu, 01-Jan-1970 00:00:10 GMT, autoLogin=0; Expires=Thu, 01-Jan-1970 00:00:10 GMT; Path=/, autoLogin=0; Expires=Thu, 01-Jan-1970 00:00:10 GMT, autoLoginNew=1; Expires=Sun, 29-Aug-2010 11:28:25 GMT; Path=/, forgetEmail=0; Expires=Tue, 19-Oct-2010 23:01:45 GMT; Path=/, email=aXdpd0BiZXJnZW5nb2NpYS5uZXQ$; Expires=Tue, 19-Oct-2010 23:01:45 GMT; Path=/, httpslogin=0; Expires=Tue, 19-Oct-2010 23:01:45 GMT; Path=/"):
    if logincookie:
      # bejelentkezés is for losers. de legalábbis nem megy.
      self.logincookie = logincookie
    else:
      loginurl = "http://iwiw.hu/pages/user/login.jsp?method=Login&&loginradio=1&email="+ email + "&password="+ password
      result = urlfetch.fetch(loginurl, follow_redirects=False)
      if (re.search("autoLoginLimited", result.headers.get('set-cookie', '')) ):
       # print result.headers.get('set-cookie', '')
        self.logincookie = result.headers.get('set-cookie', '')
      else:
        raise IwiwLoginError

