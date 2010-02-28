#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

import os
from google.appengine.ext.webapp import template
from django.utils import simplejson 

import cgi

from etr import Etr
from iwiw import Iwiw

class KurzustablaHandler(webapp.RequestHandler):
  def get(self):

    self.response.out.write('[{"kurzuskod": "BBN-ANG-342.118", "kurzusid": "650978", "cim": "A Biblia évszazadokon át"}, {"kurzuskod": "BBN-ANG-261", "kurzusid": "649424", "cim": "Alkalmazott nyelvészet előadás"}, {"kurzuskod": "BBN-ANG-215", "kurzusid": "651603", "cim": "Az angol irodalom 1890-től az 1960-as évekig"}, {"kurzuskod": "BBN-ANG-216\/d", "kurzusid": "651624", "cim": "Az angol irodalom 1890-től az 1960-as évekig"}, {"kurzuskod": "BBN-ANG-213", "kurzusid": "649386", "cim": "Az angol irodalom a restaurációtól 1890-ig"}, {"kurzuskod": "BBN-ANG-214\/d", "kurzusid": "651582", "cim": "Az angol irodalom a restaurációtól 1890-ig"}, {"kurzuskod": "BBN-AME-221", "kurzusid": "650985", "cim": "Az Egyesült Államok történelme 1"}, {"kurzuskod": "BBN-ANG-243", "kurzusid": "651149", "cim": "Haladó hangtan"}, {"kurzuskod": "BBN-ANG-253", "kurzusid": "651236", "cim": "Haladó mondattan"}, {"kurzuskod": "BBN-ANG-242\/a", "kurzusid": "651121", "cim": "Hangtan"}, {"kurzuskod": "ZBSK-02.149", "kurzusid": "651712", "cim": "Shakespeare elemzések"}, {"kurzuskod": "BBN-ANG-204\/1\/a", "kurzusid": "648772", "cim": "Tematikus nyelvfejlesztés"}]')
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
    try:
      etr = Etr(felhasznalonev, jelszo)
      cucc = []
      for kurzuskod in kurzusok: 
        nevsor = etr.listNevsor(kurzuskod)
        nevek = set(x['nev'] for x in nevsor)
        cucc.append(str(nevek))
      kozosnevek = eval(" & ".join(cucc)) # fakin undorító. halmazok metszete.
      etr.logout()
      # self.response.out.write(kozosnevek)
      
      iwiw = Iwiw()
      response = []
      for nev in kozosnevek:
	response.append(iwiw.showfirstmatch(fullname=nev))
      self.response.out.write(response)
    except NameError:
      self.response.out.write("gebasz")
      self.response.out.write(self.request.get_all("kurzus"))

class MainHandler(webapp.RequestHandler):

  def get(self):
    template_values = {
      "text" : "hello world"  
    }
    path = os.path.join(os.path.dirname(__file__), 'templates/index.html')
    self.response.out.write(template.render(path, template_values))

    

def main():
  application = webapp.WSGIApplication([('/', MainHandler),
                                        ('/etr/kurzustabla', KurzustablaHandler),
                                        ('/kozos', KozosHandler)
                                        ],
                                       debug=True)
  util.run_wsgi_app(application)


if __name__ == '__main__':
  main()
