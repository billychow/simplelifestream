import yaml,copy
from google.appengine.ext import webapp
from google.appengine.api import memcache
from dreammx.util import *
from dreammx.appengine.cache import memcache as cache

class LifeStream():
	__instance__ = None

	@staticmethod
	def instance():
		if LifeStream.__instance__ is None:
			LifeStream.__instance__ = LifeStream()
		return LifeStream.__instance__

	def __init__(self):
		self.initialized = False
		self.feeds = []
		self.config = yaml.load(open('config.yaml'))
		self.config['feeds'] = filter(lambda feed: feed['active'] == True, self.config['feeds'])

		# Initialize Feeds
		for feed in self.config['feeds']:
			args = {}
			keys = filter(lambda k: k != 'identifer' and k != 'adapter' and k != 'active', feed.keys())

			for key in keys:
				args[key] = feed[key]
			# Dynamic initialize the feed instance and append to the list
			self.feeds.append(instantiate('lifestream.feed.'+feed['adapter'], args))

	def get_feed_index(self):
		feed_index = cache.get_set_default('feed_index', 0)
		# FIXME: May caused an exception by None Value
		if feed_index > len(self.config['feeds']) - 1:
			feed_index = 0
			memcache.set('feed_index', feed_index)
		return feed_index

	def get_data(self):
		return cache.get_set_default('ls_data', {})

	def set_data(self, data, index = 0):
		ls_data = self.get_data()
		ls_data[index] = data
		memcache.set('ls_data', ls_data)

	def get_streams(self):
		return cache.get_set_default('ls_streams', [])

	def merge(self):
		streams = []
		for stream in self.get_data().itervalues():
			streams.extend(stream)
		self.sort(streams)

	def sort(self, streams):
		streams.sort(lambda x,y: cmp(y['timestamp'], x['timestamp']))
		memcache.set('ls_streams', streams)

class LifeStreamHandler(webapp.RequestHandler):
	def __init__(): pass