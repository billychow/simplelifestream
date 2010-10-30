from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.api.labs import taskqueue
from google.appengine.api import memcache
from lifestream import *

class LifeStreamQueueWorker(webapp.RequestHandler):
	def get(self):
		memcache.set('fresh_count', 0)
		indexes = LifeStream.instance().indexes
		for index in indexes:
			taskqueue.add(url='/app_worker/task', method='GET', params={'index':index})
		taskqueue.add(url='/app_worker/refresh', method='GET', countdown=10)

class LifeStreamTaskWorker(webapp.RequestHandler):
	def get(self):
		index = int(self.request.get('index'))
		LifeStream.update_feed(index)
			
class LifeStreamRefreshWorker(webapp.RequestHandler):
	def get(self):
		LifeStream.refresh_stream()
		
def main():
	application = webapp.WSGIApplication([
		('/app_worker/queue', LifeStreamQueueWorker),
		('/app_worker/task', LifeStreamTaskWorker),
		('/app_worker/refresh', LifeStreamRefreshWorker)
	], debug=True)
	util.run_wsgi_app(application)
	
if __name__ == '__main__':
	main()