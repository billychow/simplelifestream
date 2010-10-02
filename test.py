#!/usr/bin/env python

import os, sys
import time
import datetime
import operator
import yaml
import pickle
import logging

from google.appengine.ext.webapp import util
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.api import memcache
from google.appengine.api.labs import taskqueue

from lifestream import *
from lifestream.feed import *
from dreammx.util import *

class TestHandler(webapp.RequestHandler):
	def get(self, name = ''):
		if(name == ''):
			print 'null'
		else:
			getattr(self, name)()
	
	def info(self):
		self.response.out.write('Feed Size: %d <br />' % len(LifeStream.instance().feeds))
		self.response.out.write('Data Size: %d <br />' % len(LifeStream.instance().get_data()))
		self.response.out.write('Stream Size: %d <br />' % len(LifeStream.instance().get_streams()))
		for stream in LifeStream.instance().get_streams():
			#self.response.out.write('%s' % stream)
			output = static_method('lifestream.feed.'+stream['adapter'], 'parse', {'item':stream})
			self.response.out.write('%s' % output)
	
	def time(self):
		print time.time()
	
	def test(self):
		streams = []
		for stream in LifeStream.instance().get_data().itervalues():
			streams.extend(stream)
		for stream in streams:
			self.response.out.write('%s<br />' % stream['title'])
	
	def update(self):
		ls = LifeStream.instance()
		for index in range(len(ls.feeds)):
			if ls.feeds[index].update() == True and len(ls.feeds[index].data) > 0:
				ls.set_data(ls.feeds[index].data, index)
		ls.merge()

def main():
	application = webapp.WSGIApplication([
		('/test', TestHandler),
		('/test/(.*)', TestHandler)
	], debug=True)
	util.run_wsgi_app(application)
	
if __name__ == '__main__':
	main()