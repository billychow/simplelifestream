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
		self.feeds = []
		self.indexes = []
		self.hidden = []
		self.config = yaml.load(open('config.yaml'))

		# Initialize Feeds
		for index, feed in enumerate(self.config['feeds']):
			args = {}
			for key in feed.keys():
				args[key] = feed[key]
			# Dynamic initialize the feed instance and append to the list
			self.feeds.append(instantiate('lifestream.feed.'+feed['adapter'], args))
			
			if feed.has_key('visibility') and feed['visibility'] is False:
				self.hidden.append(feed['identifer'])
			if feed.has_key('disabled') and feed['disabled'] is True:
				continue
			else:
				self.indexes.append(index)

	@memoize('ls_streams')
	def get_streams(self, limit = 40):
		streams = []
		ls_streams = Stream.all().order('-timestamp').fetch(limit)
		ls_streams = filter(lambda stream: stream.identifer not in self.hidden, ls_streams)
		
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