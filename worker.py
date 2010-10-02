from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.api.labs import taskqueue
from lifestream import *

class LifeStreamQueueWorker(webapp.RequestHandler):
	def get(self):
		count = len(LifeStream.instance().feeds)
		for i in range(count):
			taskqueue.add(url='/app_worker/task', method='GET', params={'index':i})
		taskqueue.add(url='/app_worker/merge', method='GET', countdown=10)

class LifeStreamTaskWorker(webapp.RequestHandler):
	def get(self):
		ls = LifeStream.instance()
		index = int(self.request.get('index'))
		if ls.feeds[index].update() == True:
			ls.set_data(ls.feeds[index].data, index)
			
class LifeStreamMergeWorker(webapp.RequestHandler):
	def get(self):
		LifeStream.instance().merge()
		
def main():
	application = webapp.WSGIApplication([
		('/app_worker/queue', LifeStreamQueueWorker),
		('/app_worker/task', LifeStreamTaskWorker),
		('/app_worker/merge', LifeStreamMergeWorker)
	], debug=True)
	util.run_wsgi_app(application)
	
if __name__ == '__main__':
	main()