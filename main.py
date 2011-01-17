# -*- coding: utf-8 -*-

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

import os
from google.appengine.ext.webapp import template
from django.utils import simplejson 

import cgi

from etr import Etr
from iwiw import Iwiw

import logging
from google.appengine.api import memcache
from urllib import urlencode

class KurzustablaHandler(webapp.RequestHandler):
  def get(self):
     self.response.out.write('üzázs: POST felhasznalonev=[EHA kód]&jelszo=[ETR-es jelszó]')
  def post(self):
    felhasznalonev = cgi.escape(self.request.get('felhasznalonev'))
    jelszo = cgi.escape(self.request.get('jelszo'))
    
    etr = Etr(felhasznalonev, jelszo)
    kurzustabla = etr.kurzustabla()
    etr.logout()
    self.response.out.write(simplejson.dumps(kurzustabla))

class KozosHandler(webapp.RequestHandler):
  def get(self):
    self.response.out.write("post!")
  def post(self):
    felhasznalonev = cgi.escape(self.request.get('felhasznalonev'))
    jelszo = cgi.escape(self.request.get('jelszo'))
    kurzusok = self.request.get_all("kurzus")
    results = memcache.get("&".join(kurzusok))
    if results is not None:
      logging.error(results)
      self.response.out.write(results)
    else:
      etr = Etr(felhasznalonev, jelszo)
      cucc = []
      nevsorok_hackish = {}
      for kurzuskod in kurzusok: 
        nevsor = etr.listNevsor(kurzuskod)
        nevek = set(x['nev'] for x in nevsor)
        cucc.append(str(nevek))
      etr.logout()
      kozosnevek = eval(" & ".join(cucc)) # fakin undorító. halmazok metszete.
      dzsezn = simplejson.dumps(list(kozosnevek))
      memcache.add("&".join(kurzusok),dzsezn)
      self.response.out.write(dzsezn)
    
class IwiwSearch(webapp.RequestHandler):
  def get(self):
    from urllib import unquote
    query_string = self.request.query_string
    params = {}
    for param in query_string.split("&"):
      a = param.split("=")
      params[a[0]] = unquote(a[1])
    iwiw = Iwiw(logincookie=False)
    try:
      eredmeny = iwiw.search(**params)
      dzsezn = simplejson.dumps(eredmeny)
      if dzsezn == "[]":
        self.error(404)
      else:
        self.response.out.write(dzsezn)
    except UnboundLocalError:
      # ilyen akkor van, ha nincs találat.
      self.error(404)

class IwiwFirstMatch(webapp.RequestHandler):
  def get(self):
    from urllib import unquote
    query_string = self.request.query_string
    params = {}
    for param in query_string.split("&"):
      a = param.split("=")
      params[a[0]] = unquote(a[1])
    #self.response.out.write(params) 
    logging.debug(params)
    iwiw = Iwiw(logincookie=False) # TODO: miért nem jó az a süti, amit csináltam?
    logging.debug('iwiw bejelentkezés')
    eredmeny = iwiw.showfirstmatch(**params)
    logging.debug('van eredmény')
    self.response.out.write(simplejson.dumps(eredmeny))
    #self.response.out.write(eredmeny)
 
class AboutPage(webapp.RequestHandler):
  def get(self):
    aboutlap = os.path.join(os.path.dirname(__file__), 'templates/about.html')
    self.response.out.write(template.render(aboutlap, {}))
 
 

class MainHandler(webapp.RequestHandler):

  def get(self):
    path = os.path.join(os.path.dirname(__file__), 'templates/uj-index.html')
    #self.response.out.write(template.render(path, template_values))
    self.response.out.write("hamarosan, most már tényleg!")
    

def main():
  logging.getLogger().setLevel(logging.ERROR)
  application = webapp.WSGIApplication([#('/', MainHandler),
                                        ('/about', AboutPage),
                                        ('/etr/kurzustabla', KurzustablaHandler),
                                        ('/kozos', KozosHandler),
                                        ('/iwiw/firstmatch', IwiwFirstMatch),
                                        ('/iwiw/search', IwiwSearch),
                                        ],
                                       debug=False)
  util.run_wsgi_app(application)


if __name__ == '__main__':
  main()
