import os
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

class Controller(webapp.RequestHandler):
	_defaultAction = 'indexAction'
	_templatePath = 'template/'
	_defaultPackage = 'default'
	
	def dispatch(self, *args, **kwargs):
		self._action = self.__class__._defaultAction
		self._dict = {}
		self._parms = []
		self._package = None
		self.template_values = {}
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
				except Exception, e:
					self.response.out.write('ERROR: %s' % e)
					return

		return self._noRouteAction(*self._parms, **self._dict)

	def get(self, *args, **kwargs):
		return self.dispatch(*args, **kwargs)

	def post(self, *args, **kwargs):
		return self.dispatch(*args, **kwargs)

	def indexAction(self):pass

	def _noRouteAction(self, *args, **kwargs):
		print 'no route!'
	
	def get_package(self):
		if self._package is None:
			return self.__class__._defaultPackage
		return self._package
	def set_package(self, value):
		self._package = value
	
	def get_template(self, tpl, default = False):
		if default == True:
			tpl_path = self.__class__._templatePath + self.__class__._defaultPackage + '/' + tpl
		else:
			tpl_path = self.__class__._templatePath + self.get_package() + '/' + tpl

		if os.path.isfile(tpl_path) == False:
			if default == True:
				raise Exception('Template not found: %s' % tpl)
			else:
				return self.get_template(tpl, True)
		else:
			return tpl_path
		
	def render(self, template_file, output = True):
		out = template.render(self.get_template(template_file), self.template_values)
		if output == True:
			self.response.out.write(out)
		else:
			return out
