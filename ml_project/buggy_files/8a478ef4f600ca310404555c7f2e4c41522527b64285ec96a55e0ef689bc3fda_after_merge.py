	def _sort_hooks(self, hook):
		self._plugin_hooks[hook] = sorted(self._plugin_hooks[hook],
		                                  key=lambda x: (x[0] is None, sv(x[0]), sv(x[1]), sv(x[2])))