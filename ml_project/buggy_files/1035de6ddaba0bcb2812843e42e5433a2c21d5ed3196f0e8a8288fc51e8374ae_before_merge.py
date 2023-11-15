	def _find_plugins_from_folders(self, folders, existing, ignored_uninstalled=True):
		result = OrderedDict()

		for folder in folders:
			try:
				flagged_readonly = False
				if isinstance(folder, (list, tuple)):
					if len(folder) == 2:
						folder, flagged_readonly = folder
					else:
						continue
				actual_readonly = not os.access(folder, os.W_OK)

				if not os.path.exists(folder):
					self.logger.warn("Plugin folder {folder} could not be found, skipping it".format(folder=folder))
					continue

				for entry in scandir(folder):
					try:
						if entry.is_dir() and os.path.isfile(os.path.join(entry.path, "__init__.py")):
							key = entry.name
						elif entry.is_file() and entry.name.endswith(".py"):
							key = entry.name[:-3] # strip off the .py extension
							if key.startswith("__"):
								# might be an __init__.py in our plugins folder, or something else we don't want
								# to handle
								continue
						else:
							continue

						if key in existing or key in result or (ignored_uninstalled and key in self.marked_plugins["uninstalled"]):
							# plugin is already defined, ignore it
							continue

						plugin = self._import_plugin_from_module(key, folder=folder)
						if plugin:
							plugin.origin = FolderOrigin("folder", folder)
							plugin.managable = not flagged_readonly and not actual_readonly
							plugin.bundled = flagged_readonly

							plugin.enabled = False

							result[key] = plugin
					except:
						self.logger.exception("Error processing folder entry {!r} from folder {}".format(entry, folder))
			except:
				self.logger.exception("Error processing folder {}".format(folder))

		return result