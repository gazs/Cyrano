# -*- coding: utf-8 -*-

from mechanize import Browser
from BeautifulSoup import BeautifulSoup
import cookielib
import re

class Etr:
  def logout(self):
    self._browser.open("https://etr.elte.hu/etrweb/logout.asp")
  
  def kurzustabla(self):
    kurzuskodok = []
    self._browser.open("https://etr.elte.hu/etrweb/kurzustabla.asp")
    kurzustabla = self._browser.response().read()
    sorok = re.findall("<tr class=sor.*?/tr>", kurzustabla)
    for sor in sorok:
      leves = BeautifulSoup(sor)
      kurzusid = int(re.search("ckid=([0-9]*)", leves.tr.contents[0].a["href"]).group(1))
      kurzuskod = leves.tr.contents[0].a.string
      cim = leves.tr.contents[1].string
      tipus = leves.tr.contents[2].string
      eloado = leves.tr.contents[3].string
      kredit = leves.tr.contents[4].string
      oraszam = leves.tr.contents[5].string
      forumid = int(re.search("szervezo_id=([0-9]*)", leves.tr.contents[6].a["href"]).group(1))
      kurzuskodok.append({"kurzusid": kurzusid, "kurzuskod": kurzuskod, "cim": cim})
    return kurzuskodok
  
  def listNevsor(self, kurzuskod):
    nevek = []
    self._browser.open("https://etr.elte.hu/etrweb/kurz_info.asp?lista=5&ckid=" + kurzuskod)
    nevsor = BeautifulSoup( self._browser.response().read() )
    lista = nevsor.findAll("tr", { "class": "sor0" } ) + nevsor.findAll("tr", { "class": "sor2" }) # páros oszlop, páratlan oszlop, red lorry, yellow lorry
    for elem in lista:
      try:
        mailcim = elem.a["href"].replace("mailto:", "")
        nev = elem.a.string
      except TypeError: # nincs mailcím megadva
        mailcim = ""
        nev = elem.span.string
      ehakod = elem.contents[2].string
      nevek.append({"mailcim": mailcim, "nev": nev, "ehakod": ehakod})
    return nevek
  
  def __init__(self, uname, pwd):
    # TODO: mi van, ha nem jó a jelszó? 
    # TODO: mi van, ha túlterhelt az etr?
    # TODO: hibakezelés:bejelentkezés
    
    self._browser = Browser()
    cj = cookielib.LWPCookieJar()
    self._browser.set_cookiejar(cj)
    self._browser.set_handle_equiv(True)
    self._browser.set_handle_gzip(True)
    self._browser.set_handle_redirect(True)
    self._browser.set_handle_referer(True)
    self._browser.set_handle_robots(False)
    self._browser.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US) AppleWebKit/533.1 (KHTML, like Gecko) Chrome/5.0.334.0 Safari/533.1')]
    kezdolap = self._browser.open("https://etr.elte.hu/etrweb/login.asp")
    # uname= , pwd= , nyelv=0
    self._browser.select_form("form1")
    self._browser["uname"] = uname
    self._browser["pwd"] = pwd 
    login = self._browser.submit()

