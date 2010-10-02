from google.appengine.ext import db

class Stream(db.Expando):
	timestamp = db.IntegerProperty(required=True, indexed=True)
	type = db.StringProperty(required=True, indexed=True)
	identifer = db.StringProperty(required=True, indexed=True)
	origin = db.StringProperty()

class Feed(db.Model):
	identifer = db.StringProperty(required=True, indexed=True)
	title = db.StringProperty(required=True)
	last_updated = db.IntegerProperty()
	active = db.BooleanProperty()
