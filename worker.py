from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.api.labs import taskqueue
from lifestream import *

class LifeStreamQueueWorker(webapp.RequestHandler):
	def get(self):
		taskqueue.add(url='/app_worker/task', method='GET')

class LifeStreamTaskWorker(webapp.RequestHandler):
	def get(self):
		ls = LifeStream.instance()
		index = ls.get_feed_index()
		if ls.feeds[index].update() == True:
			if len(ls.feeds[index].data) > 0:
				ls.set_data(ls.feeds[index].data, index)
				ls.merge()
		memcache.incr('feed_index')
		
def main():
	application = webapp.WSGIApplication([
		('/app_worker/queue', LifeStreamQueueWorker),
		('/app_worker/task', LifeStreamTaskWorker)
	], debug=True)
	util.run_wsgi_app(application)
	
if __name__ == '__main__':
	main()