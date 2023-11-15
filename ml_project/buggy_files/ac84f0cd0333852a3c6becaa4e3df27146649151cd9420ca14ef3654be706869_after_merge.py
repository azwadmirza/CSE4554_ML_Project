	def _import_plugin(self, key, f, filename, description, name=None, version=None, summary=None, author=None, url=None, license=None, bundled=False):
		try:
			instance = imp.load_module(key, f, filename, description)
			plugin = PluginInfo(key, filename, instance, name=name, version=version, description=summary, author=author, url=url, license=license)
			plugin.bundled = bundled
		except:
			self.logger.exception("Error loading plugin {key}".format(key=key))
			return None

		if plugin.check():
			return plugin
		else:
			self.logger.warn("Plugin \"{plugin}\" did not pass check".format(plugin=str(plugin)))
			return None