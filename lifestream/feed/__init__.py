import logging
import urllib, string
from xml.dom import minidom

from google.appengine.ext import db
from google.appengine.api import memcache

from dreammx.ext import feedparser
from django.utils import simplejson
from dreammx.util import *
from lifestream.model import *

class Feed(object):
	def __init__(self, config):
		self.config = config
		if config.has_key('timezone'):
			self.config['tz_offset'] = int(config['timezone']) * 3600
		else:
			self.config['tz_offset'] = 0

	def update(self):
		raise Exception('Not implement')
		
	def save(self):
		raise Exception('Not implement')
		
	def get_last_timestamp(self):
		last_timestamp = memcache.get(self.config['identifer']+'_last_timestamp')
		if last_timestamp is not None: return last_timestamp
		
		streams = Stream.all().filter('identifer =', self.config['identifer']).filter('adapter =', self.__class__.__name__).order('-timestamp').fetch(1)
		if(len(streams) == 1):
			memcache.set(self.config['identifer']+'_last_timestamp', streams[0].timestamp)
			return streams[0].timestamp

	@staticmethod
	def parse(item = None):
		return '<li class="%s"><a href="%s">%s</a> via <a href="%s">%s</a> - <span title="%s">%s</span></li>' % (item['adapter'], item['link'], item['subject'], item['origin'], item['title'], format_timestamp(item['timestamp']), get_relative_datetime(item['timestamp']))
		
	@staticmethod
	def parse_js(item = None):
		return '<li class="%s">%s via <a href="%s">%s</a> - <span><a href="%s" title="%s">%s</a></span></li>' % (item['adapter'], item['subject'], item['origin'], item['title'], item['link'], format_timestamp(item['timestamp']), get_relative_datetime(item['timestamp']))

class RssFeed(Feed):
	def update(self):
		logging.info('UPDATE: %s' % self.config['source'])
		d = feedparser.parse(self.config['source'])
		if d.bozo == 1: return 0
		self.title = self.config.has_key('title') and self.config['title'] or d.channel.title
		self.origin = d.feed.link
		return self.save(d.entries)

	def save(self, entries):
		fresh_streams = []
		last_timestamp = self.get_last_timestamp()
		
		if last_timestamp is not None:
			entries = filter(lambda entry: get_timestamp(entry.updated_parsed)+self.config['tz_offset'] > last_timestamp, entries)
		
		for entry in entries:
			fresh_streams.append(Stream(timestamp=int(get_timestamp(entry.updated_parsed))+self.config['tz_offset'], adapter=self.__class__.__name__, identifer=self.config['identifer'], title=self.title, origin=self.origin, subject=entry.title, link=entry.link))
		db.put(fresh_streams)
		
		if len(entries) > 0:
			memcache.set(self.config['identifer']+'_last_timestamp', fresh_streams[0].timestamp)
		return len(fresh_streams)

class AtomFeed(RssFeed): pass
class BloggerFeed(AtomFeed): pass
class DeliciousFeed(RssFeed): pass
class DoubanFeed(RssFeed): pass
# @TODO: OAuth, API
class FacebookFeed(RssFeed):pass

class FlickrFeed(Feed):
	def update(self):
		try:
			d = urllib.urlopen(self.config['source'])
			content = string.join(d.readlines()).lstrip('jsonFlickrFeed(').rstrip(')')
			data = simplejson.loads(content)
			self.title = self.config.has_key('title') and self.config['title'] or data['title']
			self.origin = data['link']
			return self.save(data['items'])
		except Exception, e:
			return 0
	
	def save(self, items):
		fresh_streams = []
		last_timestamp = self.get_last_timestamp()
		
		if last_timestamp is not None:
			items = filter(lambda item: get_timestamp(feedparser._parse_date_w3dtf(item['published']))+self.config['tz_offset'] > last_timestamp, items)
		
		for item in items:
			fresh_streams.append(Stream(timestamp=int(get_timestamp(feedparser._parse_date_w3dtf(item['published'])))+self.config['tz_offset'], adapter=self.__class__.__name__, identifer=self.config['identifer'], title=self.title, origin=self.origin, subject=item['title'], link=item['link'], media=item['media']['m'], tags=item['tags']))
		db.put(fresh_streams)

class GithubFeed(AtomFeed):pass
class GoogleReaderShareFeed(AtomFeed):
	def update(self):
		logging.info('UPDATE: %s' % self.config['source'])
		d = feedparser.parse(self.config['source'])
		if d.bozo == 1: return 0
		self.title = self.config.has_key('title') and self.config['title'] or d.channel.title
		self.origin = d.feed.links[1]['href']
		
		return self.save(d.entries)

class LastFMFeed(Feed):
	def __init__(self, config):
		super(LastFMFeed, self).__init__(config)
		self.config['source'] = 'http://ws.audioscrobbler.com/1.0/user/'+self.config['username']+'/recenttracks.xml'

	def update(self):
		logging.info('UPDATE: %s' % self.config['source'])
		try:
			d = urllib.urlopen(self.config['source'])
			xml = minidom.parse(d)
			tracks = xml.getElementsByTagName('track')
			self.title = 'last.fm'
			self.origin = 'http://last.fm/user/'+self.config['username']
			return self.save(tracks)
		except Exception, e:
			return 0
		
	def save(self, tracks):
		fresh_streams = []
		last_timestamp = self.get_last_timestamp()
		
		if last_timestamp is not None:
			tracks = filter(lambda track: int(track.childNodes[11].attributes['uts'].value)+self.config['tz_offset'] > last_timestamp, tracks)
		
		for track in tracks:
			fresh_streams.append(Stream(timestamp=int(track.childNodes[11].attributes['uts'].value)+self.config['tz_offset'], adapter=self.__class__.__name__, identifer=self.config['identifer'], title=self.title, origin=self.origin, artist=track.childNodes[1].firstChild.data, subject=track.childNodes[3].firstChild.data, link=track.childNodes[9].firstChild.data))
		db.put(fresh_streams)
		
		if len(tracks) > 0:
			memcache.set(self.config['identifer']+'_last_timestamp', fresh_streams[0].timestamp)
		
		return len(fresh_streams)
		
	@staticmethod
	def parse(item = None):
		return '<li class="%s"><a href="%s">%s</a> - <a href="%s">%s</a> via <a href="%s">%s</a> - <span title="%s">%s</span></li>' % (item['adapter'], 'http://last.fm/music/'+item['artist'], item['artist'], item['link'], item['subject'], item['origin'], item['title'], format_timestamp(item['timestamp']), get_relative_datetime(item['timestamp']))

	@staticmethod
	def parse_js(item = None):
		return '<li class="%s">%s - %s via <a href="%s">%s</a> - <span><a href="%s" title="%s">%s</a></span></li>' % (item['adapter'], item['artist'], item['subject'], item['origin'], item['title'], item['link'], format_timestamp(item['timestamp']), get_relative_datetime(item['timestamp']))

class TwitterFeed(RssFeed):
	def update(self):
		logging.info('UPDATE: %s' % self.config['source'])
		d = feedparser.parse(self.config['source'])
		if d.bozo == 1: return 0
		self.title = self.config.has_key('title') and self.config['title'] or d.channel.title
		self.origin = d.channel.link
		return self.save(d.entries)

	def save(self, entries):
		fresh_streams = []
		last_timestamp = self.get_last_timestamp()
		
		if last_timestamp is not None:
			entries = filter(lambda entry: get_timestamp(entry.updated_parsed)+self.config['tz_offset'] > last_timestamp, entries)
		
		for entry in entries:
			fresh_streams.append(Stream(timestamp=int(get_timestamp(entry.updated_parsed))+self.config['tz_offset'], adapter=self.__class__.__name__, identifer=self.config['identifer'], title=self.title, origin=self.origin, subject=entry.title[entry.title.index(':')+2:].replace("\n", "<br />"), link=entry.link))
		db.put(fresh_streams)
		
		if len(entries) > 0:
			memcache.set(self.config['identifer']+'_last_timestamp', fresh_streams[0].timestamp)
		
		return len(fresh_streams)

class WordpressFeed(RssFeed):pass