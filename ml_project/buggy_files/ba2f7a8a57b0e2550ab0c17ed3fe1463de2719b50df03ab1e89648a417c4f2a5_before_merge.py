	def _restore_backup(cls, path,
	                    settings=None,
	                    plugin_manager=None,
	                    datafolder=None,
	                    on_install_plugins=None,
	                    on_report_unknown_plugins=None,
	                    on_invalid_backup=None,
	                    on_log_progress=None,
	                    on_log_error=None,
	                    on_restore_start=None,
	                    on_restore_done=None,
	                    on_restore_failed=None):
		if not is_os_compatible(["!windows"]):
			if callable(on_log_error):
				on_log_error(u"Restore is not supported on this operating system")
			if callable(on_restore_failed):
				on_restore_failed(path)
			return False

		restart_command = settings.global_get(["server", "commands", "serverRestartCommand"])

		basedir = settings._basedir
		cls._clean_dir_backup(basedir,
		                       on_log_progress=on_log_progress)

		plugin_repo = dict()
		repo_url = settings.global_get(["plugins", "pluginmanager", "repository"])
		if repo_url:
			plugin_repo = cls._get_plugin_repository_data(repo_url)

		if callable(on_restore_start):
			on_restore_start(path)

		try:

			with zipfile.ZipFile(path, "r") as zip:
				# read metadata
				try:
					metadata_zipinfo = zip.getinfo("metadata.json")
				except KeyError:
					if callable(on_invalid_backup):
						on_invalid_backup(u"Not an OctoPrint backup, lacks metadata.json")
					if callable(on_restore_failed):
						on_restore_failed(path)
					return False

				metadata_bytes = zip.read(metadata_zipinfo)
				metadata = json.loads(metadata_bytes)

				backup_version = get_comparable_version(metadata["version"], base=True)
				if backup_version > get_octoprint_version(base=True):
					if callable(on_invalid_backup):
						on_invalid_backup(u"Backup is from a newer version of OctoPrint and cannot be applied")
					if callable(on_restore_failed):
						on_restore_failed(path)
					return False

				# unzip to temporary folder
				temp = tempfile.mkdtemp()
				try:
					if callable(on_log_progress):
						on_log_progress(u"Unpacking backup to {}...".format(temp))
					abstemp = os.path.abspath(temp)
					for member in zip.infolist():
						abspath = os.path.abspath(os.path.join(temp, member.filename))
						if abspath.startswith(abstemp):
							zip.extract(member, temp)

					# sanity check
					configfile = os.path.join(temp, "basedir", "config.yaml")
					if not os.path.exists(configfile):
						if callable(on_invalid_backup):
							on_invalid_backup(u"Backup lacks config.yaml")
						if callable(on_restore_failed):
							on_restore_failed(path)
						return False

					import yaml

					with codecs.open(configfile) as f:
						configdata = yaml.safe_load(f)

					if configdata.get("accessControl", dict()).get("enabled", True):
						userfile = os.path.join(temp, "basedir", "users.yaml")
						if not os.path.exists(userfile):
							if callable(on_invalid_backup):
								on_invalid_backup(u"Backup lacks users.yaml")
							if callable(on_restore_failed):
								on_restore_failed(path)
							return False

					if callable(on_log_progress):
						on_log_progress(u"Unpacked")

					# install available plugins
					with codecs.open(os.path.join(temp, "plugin_list.json"), "r") as f:
						plugins = json.load(f)

					known_plugins = []
					unknown_plugins = []
					if plugins:
						if plugin_repo:
							for plugin in plugins:
								if plugin["key"] in plugin_manager.plugins:
									# already installed
									continue

								if plugin["key"] in plugin_repo:
									# not installed, can be installed from repository url
									known_plugins.append(plugin_repo[plugin["key"]])
								else:
									# not installed, not installable
									unknown_plugins.append(plugin)

						else:
							# no repo, all plugins are not installable
							unknown_plugins = plugins

						if callable(on_log_progress):
							if known_plugins:
								on_log_progress(u"Known and installable plugins: {}".format(u", ".join(map(lambda x: x["id"], known_plugins))))
							if unknown_plugins:
								on_log_progress(u"Unknown plugins: {}".format(u", ".join(map(lambda x: x["key"], unknown_plugins))))

						if callable(on_install_plugins):
							on_install_plugins(known_plugins)

						if callable(on_report_unknown_plugins):
							on_report_unknown_plugins(unknown_plugins)

					# move config data
					basedir_backup = basedir + ".bck"
					basedir_extracted = os.path.join(temp, "basedir")

					if callable(on_log_progress):
						on_log_progress(u"Renaming {} to {}...".format(basedir, basedir_backup))
					os.rename(basedir, basedir_backup)

					try:
						if callable(on_log_progress):
							on_log_progress(u"Moving {} to {}...".format(basedir_extracted, basedir))
						os.rename(basedir_extracted, basedir)
					except:
						if callable(on_log_error):
							on_log_error(u"Error while restoring config data", exc_info=sys.exc_info())
							on_log_error(u"Rolling back old config data")

						os.rename(basedir_backup, basedir)

						if callable(on_restore_failed):
							on_restore_failed(path)
						return False

					if unknown_plugins:
						if callable(on_log_progress):
							on_log_progress(u"Writing info file about unknown plugins")

						if not os.path.isdir(datafolder):
							os.makedirs(datafolder)

						unknown_plugins_path = os.path.join(datafolder, UNKNOWN_PLUGINS_FILE)
						try:
							with codecs.open(unknown_plugins_path, mode="w", encoding="utf-8") as f:
								json.dump(unknown_plugins, f)
						except:
							if callable(on_log_error):
								on_log_error(u"Could not persist list of unknown plugins to {}".format(unknown_plugins_path),
								             exc_info = sys.exc_info())

				finally:
					if callable(on_log_progress):
						on_log_progress(u"Removing temporary unpacked folder")
					shutil.rmtree(temp)

		except:
			exc_info = sys.exc_info()
			try:
				if callable(on_log_error):
					on_log_error(u"Error while running restore", exc_info=exc_info)
				if callable(on_restore_failed):
					on_restore_failed(path)
			finally:
				del exc_info
			return False

		finally:
			# remove zip
			if callable(on_log_progress):
				on_log_progress(u"Removing temporary zip")
			os.remove(path)

		# restart server
		if restart_command:
			import sarge

			if callable(on_log_progress):
				on_log_progress(u"Restarting...")
			if callable(on_restore_done):
				on_restore_done(path)

			try:
				sarge.run(restart_command, async_=True)
			except:
				if callable(on_log_error):
					on_log_error(u"Error while restarting via command {}".format(restart_command),
					             exc_info=sys.exc_info())
					on_log_error(u"Please restart OctoPrint manually")
				return False

		else:
			if callable(on_restore_done):
				on_restore_done(path)

		return True