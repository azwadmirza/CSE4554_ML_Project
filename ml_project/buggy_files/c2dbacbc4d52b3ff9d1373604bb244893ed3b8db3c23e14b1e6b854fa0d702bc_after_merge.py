	def _create_backup(cls, name,
	                   exclude=None,
	                   settings=None,
	                   plugin_manager=None,
	                   datafolder=None,
	                   on_backup_start=None,
	                   on_backup_done=None,
	                   on_backup_error=None):
		try:
			if exclude is None:
				exclude = []

			configfile = settings._configfile
			basedir = settings._basedir

			temporary_path = os.path.join(datafolder, ".{}".format(name))
			final_path = os.path.join(datafolder, name)

			size = cls._get_disk_size(basedir)
			if not cls._free_space(os.path.dirname(temporary_path), size):
				raise InsufficientSpace()

			own_folder = datafolder
			defaults = [os.path.join(basedir, "config.yaml"),] + \
			           [os.path.join(basedir, folder) for folder in default_settings["folder"].keys()]

			compression = zipfile.ZIP_DEFLATED if zlib else zipfile.ZIP_STORED

			if callable(on_backup_start):
				on_backup_start(name, temporary_path, exclude)

			with zipfile.ZipFile(temporary_path, mode="w", compression=compression, allowZip64=True) as zip:
				def add_to_zip(source, target, ignored=None):
					if ignored is None:
						ignored = []

					if source in ignored:
						return

					if os.path.isdir(source):
						for entry in scandir(source):
							add_to_zip(entry.path, os.path.join(target, entry.name), ignored=ignored)
					elif os.path.isfile(source):
						zip.write(source, arcname=target)

				# add metadata
				metadata = dict(version=get_octoprint_version_string(),
				                excludes=exclude)
				zip.writestr("metadata.json", json.dumps(metadata))

				# backup current config file
				add_to_zip(configfile, "basedir/config.yaml", ignored=[own_folder,])

				# backup configured folder paths
				for folder in default_settings["folder"].keys():
					if folder in exclude:
						continue

					if folder in ("generated", "logs", "watched",):
						continue

					add_to_zip(settings.global_get_basefolder(folder),
					           "basedir/" + folder.replace("_", "/"),
					           ignored=[own_folder,])

				# backup anything else that might be lying around in our basedir
				add_to_zip(basedir, "basedir", ignored=defaults + [own_folder, ])

				# add list of installed plugins
				plugins = []
				plugin_folder = settings.global_get_basefolder("plugins")
				for key, plugin in plugin_manager.plugins.items():
					if plugin.bundled or (isinstance(plugin.origin, FolderOrigin) and plugin.origin.folder == plugin_folder):
						# ignore anything bundled or from the plugins folder we already include in the backup
						continue

					plugins.append(dict(key=plugin.key,
					                    name=plugin.name,
					                    url=plugin.url))

				if len(plugins):
					zip.writestr("plugin_list.json", json.dumps(plugins))

			shutil.move(temporary_path, final_path)

			if callable(on_backup_done):
				on_backup_done(name, final_path, exclude)
		except:
			if callable(on_backup_error):
				exc_info = sys.exc_info()
				try:
					on_backup_error(name, exc_info)
				finally:
					del exc_info
			raise