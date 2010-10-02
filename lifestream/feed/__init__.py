import urllib
import logging
from xml.dom import minidom

from dreammx.ext import feedparser
from dreammx.util import *

class Feed(object):
	def __init__(self, source, title = '', enable = True):
		self.source = source
		self.title = title.strip() != '' and title.strip() or ''
		self.enable = enable
		self.data = None
		self.timestamp = None
		self.last_updated = None

	def update(self):
		raise Exception

	@staticmethod
	def parse(item = None):
		#clazz.__name__
		return '<li><a href="%s">%s</a> via <a href="%s">%s</a> - <span title="%s">%s</span></li>' % (item['link'], item['subject'], item['origin'], item['title'], format_timestamp(item['timestamp']), get_relative_datetime(item['timestamp']))
		
	@staticmethod
	def parse_js(item = None):
		return '<li>%s via <a href="%s">%s</a> - <span><a href="%s" title="%s">%s</a></span></li>' % (item['subject'], item['origin'], item['title'], item['link'], format_timestamp(item['timestamp']), get_relative_datetime(item['timestamp']))

class RssFeed(Feed):
	def update(self):
		logging.info('UPDATE: %s' % self.source)
		self.data = []
		d = feedparser.parse(self.source)
		if d.bozo == 1: return False
		self.title = self.title != '' and self.title or d.channel.title
		self.timestamp = hasattr(self, 'updated') and get_timestamp(d.updated) or get_timestamp()
		self.last_updated = get_timestamp()
		for entry in d.entries:
			self.data.append(dict(title=self.title, origin=d.feed.link, subject=entry.title, link=entry.link, author=entry.author, updated=entry.updated, timestamp=get_timestamp(entry.updated_parsed), adapter=self.__class__.__name__))
		return True

class AtomFeed(RssFeed): pass

# @TODO: OAuth, API
class FacebookFeed(RssFeed):pass

class GithubFeed(AtomFeed):pass
class GoogleReaderShareFeed(AtomFeed):
	def update(self):
		logging.info('UPDATE: %s' % self.source)
		self.data = []
		d = feedparser.parse(self.source)
		if d.bozo == 1: return False
		self.title = self.title != '' and self.title or d.channel.title
		self.timestamp = hasattr(self, 'updated') and get_timestamp(d.updated) or get_timestamp()
		self.last_updated = get_timestamp()
		for entry in d.entries:
			self.data.append(dict(title=self.title, origin=d.feed.links[1]['href'], subject=entry.title, link=entry.link, author=entry.author, updated=entry.updated, timestamp=get_timestamp(entry.updated_parsed), adapter=self.__class__.__name__))
		return True

class LastFMFeed(Feed):
	def __init__(self, username, title = '', enable = True):
		source = 'http://ws.audioscrobbler.com/1.0/user/'+username+'/recenttracks.xml'
		self.username = username
		super(LastFMFeed, self).__init__(source, title, enable)

	def update(self):
		logging.info('UPDATE: %s' % self.source)
		self.data = []
		try:
			d = urllib.urlopen(self.source)
			xml = minidom.parse(d)
			for track in xml.getElementsByTagName('track'):
				self.data.append(dict(title=self.title, origin='http://last.fm/user/'+self.username, artist=track.childNodes[1].firstChild.data, subject=track.childNodes[3].firstChild.data, link=track.childNodes[9].firstChild.data, timestamp=int(track.childNodes[11].attributes['uts'].value), adapter=self.__class__.__name__))
		except Exception, e:
			print e
			return False
		return True
		
	@staticmethod
	def parse(item = None):
		return '<li><a href="%s">%s</a> - <a href="%s">%s</a> via <a href="%s">%s</a> - <span title="%s">%s</span></li>' % ('http://last.fm/music/'+item['artist'], item['artist'], item['link'], item['subject'], item['origin'], item['title'], format_timestamp(item['timestamp']), get_relative_datetime(item['timestamp']))

	@staticmethod
	def parse_js(item = None):
		return '<li>%s - %s via <a href="%s">%s</a> - <span><a href="%s" title="%s">%s</a></span></li>' % (item['artist'], item['subject'], item['origin'], item['title'], item['link'], format_timestamp(item['timestamp']), get_relative_datetime(item['timestamp']))

class TwitterFeed(RssFeed):
	def __init__(self, username, source, title = '', enable = True):
		self.username = username
		super(TwitterFeed, self).__init__(source, title, enable)
	
	def update(self):
		logging.info('UPDATE: %s' % self.source)
		self.data = []
		d = feedparser.parse(self.source)
		if d.bozo == 1: return False
		self.title = self.title != '' and self.title or d.channel.title
		self.timestamp = hasattr(self, 'updated') and get_timestamp(d.updated) or get_timestamp()
		self.last_updated = get_timestamp()
		for entry in d.entries:
			self.data.append(dict(title=self.title, origin='http://twitter.com/'+self.username, subject=entry.title[entry.title.index(':')+2:], link=entry.link, updated=entry.updated, timestamp=get_timestamp(entry.updated_parsed), adapter=self.__class__.__name__))
		return True
