from google.appengine.ext import db

class Stream(db.Expando):
	timestamp = db.IntegerProperty(required=True, indexed=True)
	adapter = db.StringProperty(required=True, indexed=True)
	identifer = db.StringProperty(required=True, indexed=True)
	title = db.StringProperty(required=True, indexed=True)
	origin = db.StringProperty(required=True, indexed=False)
	subject = db.StringProperty(required=True)
	link = db.StringProperty(required=True)

class Counter(db.Model):
	key = db.StringProperty(required=True, indexed=True)
	value = db.IntegerProperty(required=True, indexed=True)

	@staticmethod
	def add(key, value):
		counter = Counter(key, value)
		return counter.put()

	@staticmethod
	def update(key, value):
		counter = Counter(key, value)
		return counter.save()

	@staticmethod
	def delete(key, value):
		counter = Counter.get(key)
		counter.delete()
	
	def incr(value = 1):
		self.value = self.value + value
		return self.save()

	def decr(value = 1):
		self.value = self.value - value
		return self.save()
