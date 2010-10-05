#!/usr/bin/env python

from google.appengine.ext.webapp import util
from google.appengine.ext import webapp
from django.utils import simplejson

from lifestream import *
from lifestream.feed import *
from dreammx.util import *

class APIHandler(webapp.RequestHandler):
	def get(self):
		output = 'document.write(\'<ul class="lifestream">'
		for stream in LifeStream.instance().get_streams()[:20]:
			output += static_method('lifestream.feed.'+stream['adapter'], 'parse_js', {'item':stream}).replace("'", "&#039;").replace("\n", "<br />")
		output += '</ul>\');'
		self.response.out.write('%s' % output)

class JSONHandler(webapp.RequestHandler):
	def get(self):
		self.response.out.write(simplejson.dumps(LifeStream.instance().get_streams()[:20]))
		
def main():
	application = webapp.WSGIApplication([
		('/js/lifestream\.js', APIHandler),
		('/api/lifestream\.json', JSONHandler)
	], debug=True)
	util.run_wsgi_app(application)
	
if __name__ == '__main__':
	main()