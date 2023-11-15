	def _sort_hooks(self, hook):
		self._plugin_hooks[hook] = sorted(self._plugin_hooks[hook],
		                                  key=lambda x: (x[0] is None, x[0], x[1], x[2]))