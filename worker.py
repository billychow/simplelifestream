from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.api.labs import taskqueue
from lifestream import *

class LifeStreamQueueWorker(webapp.RequestHandler):
	def get(self):
		count = len(LifeStream.instance().feeds)
		for i in range(count):
			taskqueue.add(url='/app_worker/task', method='GET', params={'index':i})
		taskqueue.add(url='/app_worker/refresh', method='GET', countdown=10)

class LifeStreamTaskWorker(webapp.RequestHandler):
	def get(self):
		ls = LifeStream.instance()
		index = int(self.request.get('index'))
		ls.feeds[index].update()
			
class LifeStreamRefreshWorker(webapp.RequestHandler):
	def get(self):
		LifeStream.instance().get_streams(True)
		
def main():
	application = webapp.WSGIApplication([
		('/app_worker/queue', LifeStreamQueueWorker),
		('/app_worker/task', LifeStreamTaskWorker),
		('/app_worker/refresh', LifeStreamRefreshWorker)
	], debug=True)
	util.run_wsgi_app(application)
	
if __name__ == '__main__':
	main()