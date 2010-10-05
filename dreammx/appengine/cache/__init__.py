from google.appengine.api import memcache

def memoize(key, time=0):
	def decorator(func):
		def wrapper(*args, **kwargs):
			data = memcache.get(key)
			if data is not None:
				return data
			data = func(*args, **kwargs)
			memcache.set(key, data, time)
			return data
		return wrapper
	return decorator