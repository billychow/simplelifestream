from google.appengine.ext import webapp

class Controller(webapp.RequestHandler):
	_defaultAction = 'indexAction'
	
	def get(self, *args, **kwargs):
		self._action = self.__class__._defaultAction
		self._dict = {}
		self._parms = []
		prev_seg = None

		if len(args) > 0:
			segments = args[0].split('/')
			for index, seg in enumerate(segments):
				if index == 0 and seg.isalpha():
					self._action = seg+'Action'
				elif index == 1 and seg != '':
					self._parms.append(seg)
				else:
					if seg.isalpha() and index % 2 == 0 and seg not in self._dict.keys():
						self._dict[seg] = []
						prev_seg = seg
					elif seg != '' and prev_seg is not None:
						self._dict[prev_seg].append(seg)

		# Looping _dict, replace the list to the value when its length equals 1
		for k,v in self._dict.iteritems():
			if len(v) == 1:
				self._dict[k] = v[-1]
				continue

		if hasattr(self, self._action):
			action_method = getattr(self, self._action)
			if callable(action_method):
				try:
					return action_method(*self._parms, **self._dict)
				except TypeError: pass

		return self._noRouteAction(*self._parms, **self._dict)

	def indexAction(self):pass

	def _noRouteAction(self, *args, **kwargs):
		print 'no route!'