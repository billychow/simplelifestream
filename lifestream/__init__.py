import yaml,logging

from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.api import memcache

from dreammx.util import *
from dreammx.appengine.cache import *

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


	@memoize('ls_streams')
	def get_streams(self, limit = 40):
		streams = []
		ls_streams = Stream.all().order('-timestamp').fetch(limit)
		
		for stream in ls_streams:
			if stream.adapter == 'LastFMFeed':
				streams.append(dict(timestamp=stream.timestamp, adapter=str(stream.adapter), title=stream.title, origin=stream.origin, artist=stream.artist, subject=stream.subject, link=stream.link))
			else:
				streams.append(dict(timestamp=stream.timestamp, adapter=str(stream.adapter), title=stream.title, origin=stream.origin, subject=stream.subject, link=stream.link))
		return streams
	
	@staticmethod
	def update_feed(index=0):
		fresh_count = memcache.get('fresh_count')
		update_count = LifeStream.instance().feeds[index].update()
		if update_count > 0:
			fresh_count += update_count
			memcache.set('fresh_count', fresh_count)
	
	@staticmethod	
	def refresh_stream():
		fresh_count = memcache.get('fresh_count')
		if fresh_count > 0:
			memcache.delete('ls_streams')