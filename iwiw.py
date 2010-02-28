# -*- coding: utf-8 -*-

import re
from google.appengine.api import urlfetch



class IwiwLoginError(Exception):
   def __str__(self):
     return "nem sikerult bejelentkezni"

class NincsTalalatError(Exception):
   def __init__(self, value):
      self.value = value
   def __str__(self):
      return repr(self.value)

class Iwiw:
  def showfirstmatch(self, fullname=None, firstName=None, lastName=None, p_country=110, ageFrom=18, gender=None, school_univ="ELTE", withPhoto=1):
    from urllib import urlencode, unquote
    url = "http://iwiw.hu/search/pages/user/ajaxsearch.jsp?"
    parameterek = urlencode({
                    "do": "AdvancedSearch",
                    "page": 0,
                    "regDateYear":2002,
		    "fullname": fullname,
                    "firstName": firstName,
                    "lastName": lastName,
                    "p_country": p_country,
                    "ageFrom": ageFrom,
                    "gender": gender,
                    "school_univ": school_univ,
                    "withPhoto": withPhoto
                  })
    url += re.sub("&[a-zA-Z]*=None", "", parameterek) # különben hozzáadja a hiányzó paraméterekre, hogy None.
    iwiwsearch = urlfetch.fetch(url, headers={'Cookie': self.logincookie}).content
    try:
      userid = re.search("userID=([0-9]*)", iwiwsearch ).group(1)
      pic_thumbnail = re.search("<img.*src=\"(.*?)\"", iwiwsearch).group(1)
      pic_popup_url = re.search("/pages/main/imageview.jsp\?.*?'", iwiwsearch).group(0).replace("&amp;", "&")
      result = {
        "userid": userid, 
        "pic_thumbnail": pic_thumbnail, 
        "pic_popup_url": pic_popup_url,
      }
      return result
    except AttributeError:
      raise NincsTalalatError(parameterek)
  def __init__(self, email="iwiw@bergengocia.net", password="asdfasdf"):
    loginurl = "http://iwiw.hu/pages/user/login.jsp?method=Login&email="+ email + "&password="+ password
    result = urlfetch.fetch(loginurl, follow_redirects=False)
    if (re.search("autoLoginLimited", result.headers.get('set-cookie', '')) ):
      self.logincookie = result.headers.get('set-cookie', '')
    else:
      raise IwiwLoginError

