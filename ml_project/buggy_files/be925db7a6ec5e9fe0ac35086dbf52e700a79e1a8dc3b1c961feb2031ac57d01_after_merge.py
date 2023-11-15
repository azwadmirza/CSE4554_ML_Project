	def handle_plugins_loaded(startup=False, initialize_implementations=True, force_reload=None):
		if not startup:
			return

		from octoprint.util import sv

		sorted_disabled_from_overlays = sorted([(key, value[0], value[1]) for key, value in disabled_from_overlays.items()], key=lambda x: (x[2] is None, sv(x[2]), sv(x[0])))

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