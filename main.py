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

class KurzustablaHandler(webapp.RequestHandler):
  def get(self):
     self.response.out.write('üzázs: POST felhasznalonev=[EHA kód]&jelszo=[ETR-es jelszó]')
#    self.response.out.write('[{"kurzuskod": "BBN-ANG-342.118", "kurzusid": "650978", "cim": "A Biblia évszazadokon át"}, {"kurzuskod": "BBN-ANG-261", "kurzusid": "649424", "cim": "Alkalmazott nyelvészet előadás"}, {"kurzuskod": "BBN-ANG-215", "kurzusid": "651603", "cim": "Az angol irodalom 1890-től az 1960-as évekig"}, {"kurzuskod": "BBN-ANG-216\/d", "kurzusid": "651624", "cim": "Az angol irodalom 1890-től az 1960-as évekig"}, {"kurzuskod": "BBN-ANG-213", "kurzusid": "649386", "cim": "Az angol irodalom a restaurációtól 1890-ig"}, {"kurzuskod": "BBN-ANG-214\/d", "kurzusid": "651582", "cim": "Az angol irodalom a restaurációtól 1890-ig"}, {"kurzuskod": "BBN-AME-221", "kurzusid": "650985", "cim": "Az Egyesült Államok történelme 1"}, {"kurzuskod": "BBN-ANG-243", "kurzusid": "651149", "cim": "Haladó hangtan"}, {"kurzuskod": "BBN-ANG-253", "kurzusid": "651236", "cim": "Haladó mondattan"}, {"kurzuskod": "BBN-ANG-242\/a", "kurzusid": "651121", "cim": "Hangtan"}, {"kurzuskod": "ZBSK-02.149", "kurzusid": "651712", "cim": "Shakespeare elemzések"}, {"kurzuskod": "BBN-ANG-204\/1\/a", "kurzusid": "648772", "cim": "Tematikus nyelvfejlesztés"}]')
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
    #try:
    etr = Etr(felhasznalonev, jelszo)
    cucc = []
    for kurzuskod in kurzusok: 
      nevsor = etr.listNevsor(kurzuskod)
      nevek = set(x['nev'] for x in nevsor)
      cucc.append(str(nevek))
    kozosnevek = eval(" & ".join(cucc)) # fakin undorító. halmazok metszete.
    etr.logout()
    self.response.out.write(simplejson.dumps(list(kozosnevek)))
    
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
      self.response.out.write(simplejson.dumps(eredmeny))
    except UnboundLocalError:
      #self.response.out.write("bla")
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
    self.response.out.write(template.render(path, template_values))
    #self.response.out.write("hamarosan, most már tényleg!")
    

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
