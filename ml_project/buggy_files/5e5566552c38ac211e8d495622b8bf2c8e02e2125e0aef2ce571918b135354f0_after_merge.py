	def reload_plugins(self, startup=False, initialize_implementations=True, force_reload=None):
		self.logger.info("Loading plugins from {folders} and installed plugin packages...".format(
			folders=", ".join(map(lambda x: x[0] if isinstance(x, tuple) else str(x), self.plugin_folders))
		))

		if force_reload is None:
			force_reload = []

		plugins = self.find_plugins(existing=dict((k, v) for k, v in self.plugins.items() if not k in force_reload))
		self.disabled_plugins.update(plugins)

		# 1st pass: loading the plugins
		for name, plugin in plugins.items():
			try:
				if not plugin.blacklisted and not plugin.forced_disabled:
					self.load_plugin(name, plugin, startup=startup, initialize_implementation=initialize_implementations)
			except PluginNeedsRestart:
				pass
			except PluginLifecycleException as e:
				self.logger.info(str(e))

		self.on_plugins_loaded(startup=startup,
							   initialize_implementations=initialize_implementations,
							   force_reload=force_reload)

		# 2nd pass: enabling those plugins that need enabling
		for name, plugin in plugins.items():
			try:
				if plugin.loaded and not plugin.forced_disabled:
					if plugin.blacklisted:
						self.logger.warn("Plugin {} is blacklisted. Not enabling it.".format(plugin))
						continue
					self.enable_plugin(name, plugin=plugin, initialize_implementation=initialize_implementations, startup=startup)
			except PluginNeedsRestart:
				pass
			except PluginLifecycleException as e:
				self.logger.info(str(e))

		self.on_plugins_enabled(startup=startup,
								initialize_implementations=initialize_implementations,
								force_reload=force_reload)

		if len(self.enabled_plugins) <= 0:
			self.logger.info("No plugins found")
		else:
			self.logger.info("Found {count} plugin(s) providing {implementations} mixin implementations, {hooks} hook handlers".format(
				count=len(self.enabled_plugins) + len(self.disabled_plugins),
				implementations=len(self.plugin_implementations),
				hooks=sum(map(lambda x: len(x), self.plugin_hooks.values()))
			))