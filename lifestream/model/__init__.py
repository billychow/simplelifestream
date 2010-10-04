from google.appengine.ext import db

class Stream(db.Expando):
	timestamp = db.IntegerProperty(required=True, indexed=True)
	adapter = db.StringProperty(required=True, indexed=True)
	identifer = db.StringProperty(required=True, indexed=True)
	title = db.StringProperty(required=True, indexed=True)
	origin = db.StringProperty(required=True, indexed=False)
	subject = db.StringProperty(required=True)
	link = db.StringProperty(required=True)
