#!/usr/bin/env python
# coding=utf-8
"""Simple Life Stream for Google App Engine
"""

__version__ = "1.0"# + "$Id$
__license__ = """Copyright (c) 2010, Billy Chow, All rights reserved."""
__author__ = "Billy Chow"
_debug = 0

import os, sys
import time, datetime
import operator
import yaml

from google.appengine.ext.webapp import util
from google.appengine.ext import webapp

from lifestream import *
from lifestream.feed import *
from dreammx.util import *

class MainPage(webapp.RequestHandler):
	def get(self):
		self.response.out.write('<link href="/static/css/style.css" rel="stylesheet" type="text/css" />')
		self.response.out.write('<ul class="lifestream">')
		for stream in LifeStream.instance().get_streams():
			entry = static_method('lifestream.feed.'+str(stream.adapter), 'parse', {'item':stream})
			self.response.out.write('%s' % entry)
		self.response.out.write('</ul>')

def main():
	application = webapp.WSGIApplication([
		('/', MainPage)
	], debug=True)
	util.run_wsgi_app(application)

if __name__ == '__main__':
	main()