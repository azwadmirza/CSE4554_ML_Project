	def _import_plugin_from_module(self, key, folder=None, module_name=None, name=None, version=None, summary=None, author=None, url=None, license=None):
		# TODO error handling
		try:
			if folder:
				module = imp.find_module(key, [folder])
			elif module_name:
				module = imp.find_module(module_name)
			else:
				return None
		except:
			self.logger.warn("Could not locate plugin {key}".format(key=key))
			return None

		if self._is_plugin_blacklisted(key) or (version is not None and self._is_plugin_version_blacklisted(key, version)):
			plugin = PluginInfo(key, module[1], None, name=name, version=version, description=summary, author=author, url=url, license=license)
			plugin.blacklisted = True
			self.logger.warn("Plugin {} is blacklisted. Not importing it, only registering a dummy entry.".format(plugin))
			return plugin

		plugin = self._import_plugin(key, *module, name=name, version=version, summary=summary, author=author, url=url, license=license)
		if plugin is None:
			return None

		if plugin.check():
			return plugin
		else:
			self.logger.warn("Plugin \"{plugin}\" did not pass check".format(plugin=str(plugin)))
			return None