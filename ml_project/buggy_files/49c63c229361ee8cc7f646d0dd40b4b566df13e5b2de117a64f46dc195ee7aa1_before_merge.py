def init_pluginsystem(settings, safe_mode=False, ignore_blacklist=True, connectivity_checker=None):
	"""Initializes the plugin manager based on the settings."""

	import os

	logger = log.getLogger(__name__ + ".startup")

	plugin_folders = [(os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "plugins")), True),
	                  settings.getBaseFolder("plugins")]
	plugin_entry_points = ["octoprint.plugin"]
	plugin_disabled_list = settings.get(["plugins", "_disabled"])

	plugin_blacklist = []
	if not ignore_blacklist and settings.getBoolean(["server", "pluginBlacklist", "enabled"]):
		plugin_blacklist = get_plugin_blacklist(settings, connectivity_checker=connectivity_checker)

	plugin_validators = []
	if safe_mode:
		def validator(phase, plugin_info):
			if phase == "after_load":
				setattr(plugin_info, "safe_mode_victim", not plugin_info.bundled)
				setattr(plugin_info, "safe_mode_enabled", False)
			elif phase == "before_enable":
				if not plugin_info.bundled:
					setattr(plugin_info, "safe_mode_enabled", True)
					return False
			return True
		plugin_validators.append(validator)

	from octoprint.plugin import plugin_manager
	pm = plugin_manager(init=True,
	                    plugin_folders=plugin_folders,
	                    plugin_entry_points=plugin_entry_points,
	                    plugin_disabled_list=plugin_disabled_list,
	                    plugin_blacklist=plugin_blacklist,
	                    plugin_validators=plugin_validators)

	settings_overlays = dict()
	disabled_from_overlays = dict()

	def handle_plugin_loaded(name, plugin):
		if plugin.instance and hasattr(plugin.instance, "__plugin_settings_overlay__"):
			plugin.needs_restart = True

			# plugin has a settings overlay, inject it
			overlay_definition = getattr(plugin.instance, "__plugin_settings_overlay__")
			if isinstance(overlay_definition, (tuple, list)):
				overlay_definition, order = overlay_definition
			else:
				order = None

			overlay = settings.load_overlay(overlay_definition)

			if "plugins" in overlay and "_disabled" in overlay["plugins"]:
				disabled_plugins = overlay["plugins"]["_disabled"]
				del overlay["plugins"]["_disabled"]
				disabled_from_overlays[name] = (disabled_plugins, order)

			settings_overlays[name] = overlay
			logger.debug("Found settings overlay on plugin {}".format(name))

	def handle_plugins_loaded(startup=False, initialize_implementations=True, force_reload=None):
		if not startup:
			return

		sorted_disabled_from_overlays = sorted([(key, value[0], value[1]) for key, value in disabled_from_overlays.items()], key=lambda x: (x[2] is None, x[2], x[0]))

		disabled_list = pm.plugin_disabled_list
		already_processed = []
		for name, addons, _ in sorted_disabled_from_overlays:
			if not name in disabled_list and not name.endswith("disabled"):
				for addon in addons:
					if addon in disabled_list:
						continue

					if addon in already_processed:
						logger.info("Plugin {} wants to disable plugin {}, but that was already processed".format(name, addon))

					if not addon in already_processed and not addon in disabled_list:
						disabled_list.append(addon)
						logger.info("Disabling plugin {} as defined by plugin {}".format(addon, name))
				already_processed.append(name)

	def handle_plugin_enabled(name, plugin):
		if name in settings_overlays:
			settings.add_overlay(settings_overlays[name])
			logger.info("Added settings overlay from plugin {}".format(name))

	pm.on_plugin_loaded = handle_plugin_loaded
	pm.on_plugins_loaded = handle_plugins_loaded
	pm.on_plugin_enabled = handle_plugin_enabled
	pm.reload_plugins(startup=True, initialize_implementations=False)
	return pm