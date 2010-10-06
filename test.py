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
from lifestream.model import *
from dreammx.util import *

class Controller(webapp.RequestHandler):
	_defaultAction = 'indexAction'
	
	def get(self, *args, **kwargs):
		action = self.__class__._defaultAction
		self._dict = {}

		if len(args) > 0:
			prev_seg = '_reserved'
			self._dict['_reserved'] = []
			segments = args[0].split('/')
			for index, seg in enumerate(segments):
				if index == 0 and seg.isalpha():
					action = seg+'Action'
					continue
				if seg.isalpha():
					prev_seg = seg
					# check if dict already have the key of segment
					if seg not in self._dict.keys():
						self._dict[seg] = []
				else:
					self._dict[prev_seg].append(seg)

		if hasattr(self, action):
			action_method = getattr(self, action)
			if callable(action_method):
				return action_method(**self._dict)

		return self._noRouteAction(*args, **self._dict)

	def indexAction(self, *args, **kwargs):pass

	def _noRouteAction(self, *args, **kwargs):
		print 'no route!'

class IndexController(Controller):
	def indexAction(self, *args, **kwargs):
		print 'index'

	def viewAction(self, *args, **kwargs):
		print 'view'

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
		t = self.request.get('t')
		if t != '':
			ts = float(t)
		else:
			ts = time.time()
		self.response.out.write('<pre>')
		self.response.out.write('Timestamp: %f\n' % ts)
		self.response.out.write('Datetime: %s' % format_timestamp(ts, 0))
		self.response.out.write('</pre>')
	
	def test(self):
		self.response.out.write('<link href="/static/css/style.css" rel="stylesheet" type="text/css" />')
		self.response.out.write('<ul class="lifestream">')
		
		streams = Stream.all().order('-timestamp').fetch(100)
		
		for stream in streams:
			entry = static_method('lifestream.feed.'+str(stream.adapter), 'parse', {'item':stream})
			self.response.out.write('%s' % entry)
		self.response.out.write('</ul>')
	
	def update(self):
		ls = LifeStream.instance()
		for index in range(len(ls.feeds)):
			if ls.feeds[index].update() == True:pass

def main():
	application = webapp.WSGIApplication([
		('/test', TestHandler),
		('/test/(.*)', TestHandler),
		('/index', IndexController),
		('/index/(.*)', IndexController)
	], debug=True)
	util.run_wsgi_app(application)
	
if __name__ == '__main__':
	main()