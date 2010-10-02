import sys
import time
import datetime

def get_timestamp(time_tuple = None, tz = 0):
	if time_tuple is None: return int(time.time()) + 3600 * tz
	return int(time.mktime(time_tuple)) + 3600 * tz
	
def format_timestamp(ts, tz = 8):
	return datetime.datetime.fromtimestamp(float(ts) + 3600 * tz).strftime('%Y-%m-%d %H:%M:%S')
	
def get_relative_datetime(ts, tz = 0):
	min = 60
	hour = min * 60
	day = hour * 24
	week = day * 7
	month = day * 30
	year = month * 12
	ts = int(ts)
	now = int(time.time()) + tz * 3600
	diff = now - ts
	
	span_year = diff / year
	span_month = diff / month
	span_week = diff / week
	span_day = diff / day
	span_hour = diff / hour
	span_min = diff / min
	
	if diff > 0:
		if span_year == 1:
			return 'about one year ago'
		elif span_year > 1:
			return 'about %d years ago' % span_year
		
		if span_month == 1:
			return 'about one month ago'
		elif span_month > 1:
			return 'about %d months ago' % span_month
			
		if span_week == 1:
			return 'about one week ago'
		elif span_week > 1:
			return 'about %d weeks ago' % span_week
			
		if span_day == 1:
			return 'yesterday'
		elif span_day > 1:
			return 'about %d days ago' % span_day
			
		if span_hour == 1:
			return 'about one hour ago'
		elif span_hour > 1:
			return 'about %d hours ago' % span_hour
			
		if span_min == 1:
			return 'one minute ago'
		elif span_min > 1:
			return '%d minutes ago' % span_min
			
		if diff <= 30:
			return 'just now'
		else:
			return '%d seconds ago' % diff

	else:
		return 'in future...'


def instantiate(str, args = {}):
	path = str.split('.')
	modulename = '.'.join(path[:-1])
	classname = path[-1]

	#__import__(modulename)
	from_module = __import__(modulename, globals(), locals(), [modulename])

	#return getattr(sys.modules[modulename], classname)(**args)
	return getattr(from_module, classname)(**args)

def static_method(str, method, args = {}):
	path = str.split('.')
	modulename = '.'.join(path[:-1])
	classname = path[-1]

	from_module = __import__(modulename, globals(), locals(), [modulename])

	clazz = getattr(from_module, classname)
	return getattr(clazz, method)(**args)