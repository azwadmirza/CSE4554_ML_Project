	def _import_plugin_from_module(self, key, folder=None, module_name=None, name=None, version=None, summary=None,
	                               author=None, url=None, license=None, bundled=False):
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

		# Create a simple dummy entry first ...
		plugin = PluginInfo(key, module[1], None, name=name, version=version, description=summary, author=author,
		                    url=url, license=license)
		plugin.bundled = bundled

		if self._is_plugin_disabled(key):
			self.logger.info("Plugin {} is disabled.".format(plugin))
			plugin.forced_disabled = True

		if self._is_plugin_blacklisted(key) or (version is not None and self._is_plugin_version_blacklisted(key, version)):
			self.logger.warn("Plugin {} is blacklisted.".format(plugin))
			plugin.blacklisted = True

		if not plugin.validate("before_import", additional_validators=self.plugin_validators):
			return plugin

		# ... then create and return the real one
		return self._import_plugin(key, *module,
		                           name=name, version=version, summary=summary, author=author, url=url,
		                           license=license, bundled=bundled)