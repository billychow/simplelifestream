from google.appengine.api import memcache

def get_set_default(key, default=None):
	value = memcache.get(key)
	if value is not None:
		return value
	memcache.set(key, default)
	return default
