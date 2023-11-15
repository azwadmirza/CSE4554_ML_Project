	def set(self, path, value, force=False, defaults=None, config=None, preprocessors=None, error_on_path=False, *args, **kwargs):
		if not path:
			if error_on_path:
				raise NoSuchSettingsPath()
			return

		if self._mtime is not None and self.last_modified != self._mtime:
			self.load()

		if config is not None or defaults is not None:
			if config is None:
				config = self._config

			if defaults is None:
				defaults = dict(self._map.parents)

			chain = HierarchicalChainMap(config, defaults)
		else:
			chain = self._map

		if preprocessors is None:
			preprocessors = self._set_preprocessors

		preprocessor = None
		try:
			preprocessor = self._get_by_path(path, preprocessors)
		except NoSuchSettingsPath:
			pass

		if callable(preprocessor):
			value = preprocessor(value)

		try:
			current = chain.get_by_path(path)
		except KeyError:
			current = None

		try:
			default_value = chain.get_by_path(path, only_defaults=True)
		except KeyError:
			if error_on_path:
				raise NoSuchSettingsPath()
			default_value = None

		in_local = chain.has_path(path, only_local=True)
		in_defaults = chain.has_path(path, only_defaults=True)

		if not force and in_defaults and in_local and default_value == value:
			try:
				chain.del_by_path(path)
				self._dirty = True
				self._dirty_time = time.time()
			except KeyError:
				if error_on_path:
					raise NoSuchSettingsPath()
				pass
		elif force or (not in_local and in_defaults and default_value != value) or (in_local and current != value):
			if value is None and in_local:
				chain.del_by_path(path)
			else:
				chain.set_by_path(path, value)
			self._dirty = True
			self._dirty_time = time.time()