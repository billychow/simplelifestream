import logging
import urllib
from xml.dom import minidom

from google.appengine.ext import db
from google.appengine.api import memcache

from dreammx.ext import feedparser
from dreammx.util import *
from lifestream.model import *

class Feed(object):
	def __init__(self, source, identifer = '', title = '', timezone = 0, enable = True):
		self.source = source
		self.identifer = identifer
		self.title = title.strip() != '' and title.strip() or ''
		self.origin = ''
		self.enable = enable
		self.timestamp = None
		self.timezone = int(timezone)
		self.tz_offset = self.timezone * 3600

	def update(self):
		raise Exception()
		
	def save(self):
		raise Exception()
		
	def get_last_timestamp(self):
		last_timestamp = memcache.get(self.identifer+'_last_timestamp')
		if last_timestamp is not None: return last_timestamp
		
		streams = Stream.all().filter('identifer =', self.identifer).filter('adapter =', self.__class__.__name__).order('-timestamp').fetch(1)
		if(len(streams) == 1):
			memcache.set(self.identifer+'_last_timestamp', streams[0].timestamp)
			return streams[0].timestamp

	@staticmethod
	def parse(item = None):
		return '<li class="%s"><a href="%s">%s</a> via <a href="%s">%s</a> - <span title="%s">%s</span></li>' % (item['adapter'], item['link'], item['subject'], item['origin'], item['title'], format_timestamp(item['timestamp']), get_relative_datetime(item['timestamp']))
		
	@staticmethod
	def parse_js(item = None):
		return '<li class="%s">%s via <a href="%s">%s</a> - <span><a href="%s" title="%s">%s</a></span></li>' % (item['adapter'], item['subject'], item['origin'], item['title'], item['link'], format_timestamp(item['timestamp']), get_relative_datetime(item['timestamp']))

class RssFeed(Feed):
	def update(self):
		logging.info('UPDATE: %s' % self.source)
		d = feedparser.parse(self.source)
		if d.bozo == 1: return 0
		self.title = self.title != '' and self.title or d.channel.title
		self.origin = d.feed.link
		self.timestamp = int(get_updated_timestamp(d))+self.tz_offset
		return self.save(d.entries)

	def save(self, entries):
		fresh_streams = []
		last_timestamp = self.get_last_timestamp()
		
		if last_timestamp is not None:
			entries = filter(lambda entry: get_timestamp(entry.updated_parsed)+self.tz_offset > last_timestamp, entries)
		
		for entry in entries:
			fresh_streams.append(Stream(timestamp=int(get_timestamp(entry.updated_parsed))+self.tz_offset, adapter=self.__class__.__name__, identifer=self.identifer, title=self.title, origin=self.origin, subject=entry.title, link=entry.link))
		db.put(fresh_streams)
		
		if len(entries) > 0:
			memcache.set(self.identifer+'_last_timestamp', fresh_streams[0].timestamp)
		return len(fresh_streams)

class AtomFeed(RssFeed): pass

class BloggerFeed(AtomFeed): pass
class DoubanFeed(RssFeed): pass
# @TODO: OAuth, API
class FacebookFeed(RssFeed):pass

class GithubFeed(AtomFeed):pass
class GoogleReaderShareFeed(AtomFeed):
	def update(self):
		logging.info('UPDATE: %s' % self.source)
		d = feedparser.parse(self.source)
		if d.bozo == 1: return 0
		self.title = self.title != '' and self.title or d.channel.title
		self.origin = d.feed.links[1]['href']
		self.timestamp = int(get_updated_timestamp(d))+self.tz_offset
		
		return self.save(d.entries)

class LastFMFeed(Feed):
	def __init__(self, username, identifer = '', title = '', timezone = 0, enable = True):
		source = 'http://ws.audioscrobbler.com/1.0/user/'+username+'/recenttracks.xml'
		self.username = username
		super(LastFMFeed, self).__init__(source, identifer, title, timezone, enable)

	def update(self):
		logging.info('UPDATE: %s' % self.source)
		self.origin = 'http://last.fm/user/'+self.username
		try:
			d = urllib.urlopen(self.source)
			xml = minidom.parse(d)
			tracks = xml.getElementsByTagName('track')
			return self.save(tracks)
		except Exception, e:
			return 0
		
	def save(self, tracks):
		fresh_streams = []
		last_timestamp = self.get_last_timestamp()
		
		if last_timestamp is not None:
			tracks = filter(lambda track: int(track.childNodes[11].attributes['uts'].value)+self.tz_offset > last_timestamp, tracks)
		
		for track in tracks:
			fresh_streams.append(Stream(timestamp=int(track.childNodes[11].attributes['uts'].value)+self.tz_offset, adapter=self.__class__.__name__, identifer=self.identifer, title=self.title, origin=self.origin, artist=track.childNodes[1].firstChild.data, subject=track.childNodes[3].firstChild.data, link=track.childNodes[9].firstChild.data))
		db.put(fresh_streams)
		
		if len(tracks) > 0:
			memcache.set(self.identifer+'_last_timestamp', fresh_streams[0].timestamp)
		
		return len(fresh_streams)
		
	@staticmethod
	def parse(item = None):
		return '<li class="%s"><a href="%s">%s</a> - <a href="%s">%s</a> via <a href="%s">%s</a> - <span title="%s">%s</span></li>' % (item['adapter'], 'http://last.fm/music/'+item['artist'], item['artist'], item['link'], item['subject'], item['origin'], item['title'], format_timestamp(item['timestamp']), get_relative_datetime(item['timestamp']))

	@staticmethod
	def parse_js(item = None):
		return '<li class="%s">%s - %s via <a href="%s">%s</a> - <span><a href="%s" title="%s">%s</a></span></li>' % (item['adapter'], item['artist'], item['subject'], item['origin'], item['title'], item['link'], format_timestamp(item['timestamp']), get_relative_datetime(item['timestamp']))

class TwitterFeed(RssFeed):
	def __init__(self, username, source, identifer = '', title = '', timezone = 0, enable = True):
		self.username = username
		super(TwitterFeed, self).__init__(source, identifer, title, timezone, enable)
	
	def update(self):
		logging.info('UPDATE: %s' % self.source)
		d = feedparser.parse(self.source)
		if d.bozo == 1: return 0
		self.title = self.title != '' and self.title or d.channel.title
		self.origin = origin='http://twitter.com/'+self.username
		self.timestamp = int(get_updated_timestamp(d))+self.tz_offset
		return self.save(d.entries)

	def save(self, entries):
		fresh_streams = []
		last_timestamp = self.get_last_timestamp()
		
		if last_timestamp is not None:
			entries = filter(lambda entry: get_timestamp(entry.updated_parsed)+self.tz_offset > last_timestamp, entries)
		
		for entry in entries:
			fresh_streams.append(Stream(timestamp=int(get_timestamp(entry.updated_parsed))+self.tz_offset, adapter=self.__class__.__name__, identifer=self.identifer, title=self.title, origin=self.origin, subject=entry.title[entry.title.index(':')+2:].replace("\n", "<br />"), link=entry.link))
		db.put(fresh_streams)
		
		if len(entries) > 0:
			memcache.set(self.identifer+'_last_timestamp', fresh_streams[0].timestamp)
		
		return len(fresh_streams)

class WordpressFeed(RssFeed):pass

def get_updated_timestamp(data):
	if hasattr(data, 'updated'):
		return get_timestamp(data.updated)
	elif hasattr(data, 'feed') and hasattr(data.feed, 'updated_parsed'):
		return get_timestamp(data.feed.updated_parsed)
	else:
		return get_timestamp()