import yaml,copy,logging

from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.api import memcache

from dreammx.util import *
from dreammx.appengine.cache import memcache as cache

from lifestream.model import *

class LifeStream():
	_instance = None

	@staticmethod
	def instance():
		if LifeStream._instance is None:
			LifeStream._instance = LifeStream()
		return LifeStream._instance

	def __init__(self):
		self.initialized = False
		self.feeds = []
		self.config = yaml.load(open('config.yaml'))
		self.config['feeds'] = filter(lambda feed: feed['active'] == True, self.config['feeds'])

		# Initialize Feeds
		for feed in self.config['feeds']:
			args = {}
			keys = filter(lambda k: k != 'adapter' and k != 'active', feed.keys())

			for key in keys:
				args[key] = feed[key]
			# Dynamic initialize the feed instance and append to the list
			self.feeds.append(instantiate('lifestream.feed.'+feed['adapter'], args))


	def get_streams(self, force = False, limit = 100):
		if force == True:
			memcache.delete('ls_streams')
		ls_streams = memcache.get('ls_streams')
		if ls_streams is None:
			ls_streams = Stream.all().order('-timestamp').fetch(limit)
			memcache.set('ls_streams', ls_streams)
		return ls_streams

	def sort(self, streams):
		streams.sort(lambda x,y: cmp(y['timestamp'], x['timestamp']))
		memcache.set('ls_streams', streams)