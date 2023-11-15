	def run(self):
		if not self._allow_root:
			self._check_for_root()

		if self._settings is None:
			self._settings = settings()
		if self._plugin_manager is None:
			self._plugin_manager = octoprint.plugin.plugin_manager()

		global app
		global babel

		global printer
		global printerProfileManager
		global fileManager
		global slicingManager
		global analysisQueue
		global userManager
		global eventManager
		global loginManager
		global pluginManager
		global appSessionManager
		global pluginLifecycleManager
		global preemptiveCache
		global connectivityChecker
		global debug
		global safe_mode

		from tornado.ioloop import IOLoop
		from tornado.web import Application

		debug = self._debug
		safe_mode = self._safe_mode

		self._logger = logging.getLogger(__name__)
		pluginManager = self._plugin_manager

		# monkey patch a bunch of stuff
		util.tornado.fix_ioloop_scheduling()
		util.flask.enable_additional_translations(additional_folders=[self._settings.getBaseFolder("translations")])

		# setup app
		self._setup_app(app)

		# setup i18n
		self._setup_i18n(app)

		if self._settings.getBoolean(["serial", "log"]):
			# enable debug logging to serial.log
			logging.getLogger("SERIAL").setLevel(logging.DEBUG)

		# start the intermediary server
		self._start_intermediary_server()

		### IMPORTANT!
		###
		### Best do not start any subprocesses until the intermediary server shuts down again or they MIGHT inherit the
		### open port and prevent us from firing up Tornado later.
		###
		### The intermediary server's socket should have the CLOSE_EXEC flag (or its equivalent) set where possible, but
		### we can only do that if fcntl is availabel or we are on Windows, so better safe than sorry.
		###
		### See also issues #2035 and #2090

		# then initialize the plugin manager
		pluginManager.reload_plugins(startup=True, initialize_implementations=False)

		printerProfileManager = PrinterProfileManager()
		eventManager = self._event_manager
		analysisQueue = octoprint.filemanager.analysis.AnalysisQueue()
		slicingManager = octoprint.slicing.SlicingManager(self._settings.getBaseFolder("slicingProfiles"), printerProfileManager)

		storage_managers = dict()
		storage_managers[octoprint.filemanager.FileDestinations.LOCAL] = octoprint.filemanager.storage.LocalFileStorage(self._settings.getBaseFolder("uploads"))

		fileManager = octoprint.filemanager.FileManager(analysisQueue, slicingManager, printerProfileManager, initial_storage_managers=storage_managers)
		appSessionManager = util.flask.AppSessionManager()
		pluginLifecycleManager = LifecycleManager(pluginManager)
		preemptiveCache = PreemptiveCache(os.path.join(self._settings.getBaseFolder("data"), "preemptive_cache_config.yaml"))

		connectivityChecker = self._connectivity_checker

		def on_settings_update(*args, **kwargs):
			# make sure our connectivity checker runs with the latest settings
			connectivityEnabled = self._settings.getBoolean(["server", "onlineCheck", "enabled"])
			connectivityInterval = self._settings.getInt(["server", "onlineCheck", "interval"])
			connectivityHost = self._settings.get(["server", "onlineCheck", "host"])
			connectivityPort = self._settings.getInt(["server", "onlineCheck", "port"])

			if connectivityChecker.enabled != connectivityEnabled \
					or connectivityChecker.interval != connectivityInterval \
					or connectivityChecker.host != connectivityHost \
					or connectivityChecker.port != connectivityPort:
				connectivityChecker.enabled = connectivityEnabled
				connectivityChecker.interval = connectivityInterval
				connectivityChecker.host = connectivityHost
				connectivityChecker.port = connectivityPort
				connectivityChecker.check_immediately()

		eventManager.subscribe(events.Events.SETTINGS_UPDATED, on_settings_update)

		# setup access control
		userManagerName = self._settings.get(["accessControl", "userManager"])
		try:
			clazz = octoprint.util.get_class(userManagerName)
			userManager = clazz()
		except:
			self._logger.exception("Could not instantiate user manager {}, falling back to FilebasedUserManager!".format(userManagerName))
			userManager = octoprint.users.FilebasedUserManager()
		finally:
			userManager.enabled = self._settings.getBoolean(["accessControl", "enabled"])

		components = dict(
			plugin_manager=pluginManager,
			printer_profile_manager=printerProfileManager,
			event_bus=eventManager,
			analysis_queue=analysisQueue,
			slicing_manager=slicingManager,
			file_manager=fileManager,
			app_session_manager=appSessionManager,
			plugin_lifecycle_manager=pluginLifecycleManager,
			preemptive_cache=preemptiveCache,
			connectivity_checker=connectivityChecker,
			environment_detector=self._environment_detector
		)

		# create user manager instance
		user_manager_factories = pluginManager.get_hooks("octoprint.users.factory")
		for name, factory in user_manager_factories.items():
			try:
				userManager = factory(components, self._settings)
				if userManager is not None:
					self._logger.debug("Created user manager instance from factory {}".format(name))
					break
			except:
				self._logger.exception("Error while creating user manager instance from factory {}".format(name))
		else:
			name = self._settings.get(["accessControl", "userManager"])
			try:
				clazz = octoprint.util.get_class(name)
				userManager = clazz()
			except:
				self._logger.exception(
					"Could not instantiate user manager {}, falling back to FilebasedUserManager!".format(name))
				userManager = octoprint.users.FilebasedUserManager()
			finally:
				userManager.enabled = self._settings.getBoolean(["accessControl", "enabled"])
		components.update(dict(user_manager=userManager))

		# create printer instance
		printer_factories = pluginManager.get_hooks("octoprint.printer.factory")
		for name, factory in printer_factories.items():
			try:
				printer = factory(components)
				if printer is not None:
					self._logger.debug("Created printer instance from factory {}".format(name))
					break
			except:
				self._logger.exception("Error while creating printer instance from factory {}".format(name))
		else:
			printer = Printer(fileManager, analysisQueue, printerProfileManager)
		components.update(dict(printer=printer))

		def octoprint_plugin_inject_factory(name, implementation):
			"""Factory for injections for all OctoPrintPlugins"""
			if not isinstance(implementation, octoprint.plugin.OctoPrintPlugin):
				return None
			props = dict()
			props.update(components)
			props.update(dict(
				data_folder=os.path.join(self._settings.getBaseFolder("data"), name)
			))
			return props

		def settings_plugin_inject_factory(name, implementation):
			"""Factory for additional injections/initializations depending on plugin type"""
			if not isinstance(implementation, octoprint.plugin.SettingsPlugin):
				return

			default_settings_overlay = dict(plugins=dict())
			default_settings_overlay["plugins"][name] = implementation.get_settings_defaults()
			self._settings.add_overlay(default_settings_overlay, at_end=True)

			plugin_settings = octoprint.plugin.plugin_settings_for_settings_plugin(name, implementation)
			if plugin_settings is None:
				return

			return dict(settings=plugin_settings)

		def settings_plugin_config_migration_and_cleanup(identifier, implementation):
			"""Take care of migrating and cleaning up any old settings"""

			if not isinstance(implementation, octoprint.plugin.SettingsPlugin):
				return

			settings_version = implementation.get_settings_version()
			settings_migrator = implementation.on_settings_migrate

			if settings_version is not None and settings_migrator is not None:
				stored_version = implementation._settings.get_int([octoprint.plugin.SettingsPlugin.config_version_key])
				if stored_version is None or stored_version < settings_version:
					settings_migrator(settings_version, stored_version)
					implementation._settings.set_int([octoprint.plugin.SettingsPlugin.config_version_key], settings_version, force=True)

			implementation.on_settings_cleanup()
			implementation._settings.save()

			implementation.on_settings_initialized()

		pluginManager.implementation_inject_factories=[octoprint_plugin_inject_factory,
		                                               settings_plugin_inject_factory]
		pluginManager.initialize_implementations()

		settingsPlugins = pluginManager.get_implementations(octoprint.plugin.SettingsPlugin)
		for implementation in settingsPlugins:
			try:
				settings_plugin_config_migration_and_cleanup(implementation._identifier, implementation)
			except:
				self._logger.exception("Error while trying to migrate settings for plugin {}, ignoring it".format(implementation._identifier))

		pluginManager.implementation_post_inits=[settings_plugin_config_migration_and_cleanup]

		pluginManager.log_all_plugins()

		# log environment data now
		self._environment_detector.log_detected_environment()

		# initialize file manager and register it for changes in the registered plugins
		fileManager.initialize()
		pluginLifecycleManager.add_callback(["enabled", "disabled"], lambda name, plugin: fileManager.reload_plugins())

		# initialize slicing manager and register it for changes in the registered plugins
		slicingManager.initialize()
		pluginLifecycleManager.add_callback(["enabled", "disabled"], lambda name, plugin: slicingManager.reload_slicers())

		# setup jinja2
		self._setup_jinja2()

		# make sure plugin lifecycle events relevant for jinja2 are taken care of
		def template_enabled(name, plugin):
			if plugin.implementation is None or not isinstance(plugin.implementation, octoprint.plugin.TemplatePlugin):
				return
			self._register_additional_template_plugin(plugin.implementation)
		def template_disabled(name, plugin):
			if plugin.implementation is None or not isinstance(plugin.implementation, octoprint.plugin.TemplatePlugin):
				return
			self._unregister_additional_template_plugin(plugin.implementation)
		pluginLifecycleManager.add_callback("enabled", template_enabled)
		pluginLifecycleManager.add_callback("disabled", template_disabled)

		# setup assets
		self._setup_assets()

		# configure timelapse
		octoprint.timelapse.configure_timelapse()

		# setup command triggers
		events.CommandTrigger(printer)
		if self._debug:
			events.DebugEventListener()

		loginManager = LoginManager()
		loginManager.session_protection = "strong"
		loginManager.user_callback = load_user
		if not userManager.enabled:
			loginManager.anonymous_user = users.DummyUser
			principals.identity_loaders.appendleft(users.dummy_identity_loader)
		loginManager.init_app(app, add_context_processor=False)

		# register API blueprint
		self._setup_blueprints()

		## Tornado initialization starts here

		if self._host is None:
			self._host = self._settings.get(["server", "host"])
		if self._port is None:
			self._port = self._settings.getInt(["server", "port"])

		ioloop = IOLoop()
		ioloop.install()

		self._router = SockJSRouter(self._create_socket_connection, "/sockjs",
		                            session_kls=util.sockjs.ThreadSafeSession)

		upload_suffixes = dict(name=self._settings.get(["server", "uploads", "nameSuffix"]), path=self._settings.get(["server", "uploads", "pathSuffix"]))

		def mime_type_guesser(path):
			from octoprint.filemanager import get_mime_type
			return get_mime_type(path)

		def download_name_generator(path):
			metadata = fileManager.get_metadata("local", path)
			if metadata and "display" in metadata:
				return metadata["display"]

		download_handler_kwargs = dict(
			as_attachment=True,
			allow_client_caching=False
		)

		additional_mime_types=dict(mime_type_guesser=mime_type_guesser)

		admin_validator = dict(access_validation=util.tornado.access_validation_factory(app, loginManager, util.flask.admin_validator))
		user_validator = dict(access_validation=util.tornado.access_validation_factory(app, loginManager, util.flask.user_validator))

		no_hidden_files_validator = dict(path_validation=util.tornado.path_validation_factory(lambda path: not octoprint.util.is_hidden_path(path),
		                                                                                      status_code=404))

		def joined_dict(*dicts):
			if not len(dicts):
				return dict()

			joined = dict()
			for d in dicts:
				joined.update(d)
			return joined

		util.tornado.RequestlessExceptionLoggingMixin.LOG_REQUEST = debug

		server_routes = self._router.urls + [
			# various downloads
			# .mpg and .mp4 timelapses:
			(r"/downloads/timelapse/([^/]*\.mp[g4])", util.tornado.LargeResponseHandler, joined_dict(dict(path=self._settings.getBaseFolder("timelapse")),
			                                                                                      download_handler_kwargs,
			                                                                                      no_hidden_files_validator)),
			(r"/downloads/files/local/(.*)", util.tornado.LargeResponseHandler, joined_dict(dict(path=self._settings.getBaseFolder("uploads"),
			                                                                                     as_attachment=True,
			                                                                                     name_generator=download_name_generator),
			                                                                                download_handler_kwargs,
			                                                                                no_hidden_files_validator,
			                                                                                additional_mime_types)),
			(r"/downloads/logs/([^/]*)", util.tornado.LargeResponseHandler, joined_dict(dict(path=self._settings.getBaseFolder("logs")),
			                                                                            download_handler_kwargs,
			                                                                            admin_validator)),
			# camera snapshot
			(r"/downloads/camera/current", util.tornado.UrlProxyHandler, joined_dict(dict(url=self._settings.get(["webcam", "snapshot"]),
			                                                                              as_attachment=True),
			                                                                         user_validator)),
			# generated webassets
			(r"/static/webassets/(.*)", util.tornado.LargeResponseHandler, dict(path=os.path.join(self._settings.getBaseFolder("generated"), "webassets"))),

			# online indicators - text file with "online" as content and a transparent gif
			(r"/online.txt", util.tornado.StaticDataHandler, dict(data="online\n")),
			(r"/online.gif", util.tornado.StaticDataHandler, dict(data=bytes(base64.b64decode("R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7")),
			                                                      content_type="image/gif"))
		]

		# fetch additional routes from plugins
		for name, hook in pluginManager.get_hooks("octoprint.server.http.routes").items():
			try:
				result = hook(list(server_routes))
			except:
				self._logger.exception("There was an error while retrieving additional server routes from plugin hook {name}".format(**locals()))
			else:
				if isinstance(result, (list, tuple)):
					for entry in result:
						if not isinstance(entry, tuple) or not len(entry) == 3:
							continue
						if not isinstance(entry[0], basestring):
							continue
						if not isinstance(entry[2], dict):
							continue

						route, handler, kwargs = entry
						route = r"/plugin/{name}/{route}".format(name=name, route=route if not route.startswith("/") else route[1:])

						self._logger.debug("Adding additional route {route} handled by handler {handler} and with additional arguments {kwargs!r}".format(**locals()))
						server_routes.append((route, handler, kwargs))

		headers =         {"X-Robots-Tag": "noindex, nofollow, noimageindex"}
		removed_headers = ["Server"]

		server_routes.append((r".*", util.tornado.UploadStorageFallbackHandler, dict(fallback=util.tornado.WsgiInputContainer(app.wsgi_app,
		                                                                                                                      headers=headers,
		                                                                                                                      removed_headers=removed_headers),
		                                                                             file_prefix="octoprint-file-upload-",
		                                                                             file_suffix=".tmp",
		                                                                             suffixes=upload_suffixes)))

		transforms = [util.tornado.GlobalHeaderTransform.for_headers("OctoPrintGlobalHeaderTransform",
		                                                             headers=headers,
		                                                             removed_headers=removed_headers)]

		self._tornado_app = Application(handlers=server_routes,
		                                transforms=transforms)
		max_body_sizes = [
			("POST", r"/api/files/([^/]*)", self._settings.getInt(["server", "uploads", "maxSize"])),
			("POST", r"/api/languages", 5 * 1024 * 1024)
		]

		# allow plugins to extend allowed maximum body sizes
		for name, hook in pluginManager.get_hooks("octoprint.server.http.bodysize").items():
			try:
				result = hook(list(max_body_sizes))
			except:
				self._logger.exception("There was an error while retrieving additional upload sizes from plugin hook {name}".format(**locals()))
			else:
				if isinstance(result, (list, tuple)):
					for entry in result:
						if not isinstance(entry, tuple) or not len(entry) == 3:
							continue
						if not entry[0] in util.tornado.UploadStorageFallbackHandler.BODY_METHODS:
							continue
						if not isinstance(entry[2], int):
							continue

						method, route, size = entry
						route = r"/plugin/{name}/{route}".format(name=name, route=route if not route.startswith("/") else route[1:])

						self._logger.debug("Adding maximum body size of {size}B for {method} requests to {route})".format(**locals()))
						max_body_sizes.append((method, route, size))

		self._stop_intermediary_server()

		# initialize and bind the server
		self._server = util.tornado.CustomHTTPServer(self._tornado_app, max_body_sizes=max_body_sizes, default_max_body_size=self._settings.getInt(["server", "maxSize"]))
		self._server.listen(self._port, address=self._host)

		### From now on it's ok to launch subprocesses again

		eventManager.fire(events.Events.STARTUP)

		# analysis backlog
		fileManager.process_backlog()

		# auto connect
		if self._settings.getBoolean(["serial", "autoconnect"]):
			try:
				(port, baudrate) = self._settings.get(["serial", "port"]), self._settings.getInt(["serial", "baudrate"])
				printer_profile = printerProfileManager.get_default()
				connectionOptions = printer.__class__.get_connection_options()
				if port in connectionOptions["ports"] or port == "AUTO":
						printer.connect(port=port, baudrate=baudrate, profile=printer_profile["id"] if "id" in printer_profile else "_default")
			except:
				self._logger.exception("Something went wrong while attempting to automatically connect to the printer")

		# start up watchdogs
		if self._settings.getBoolean(["feature", "pollWatched"]):
			# use less performant polling observer if explicitely configured
			observer = PollingObserver()
		else:
			# use os default
			observer = Observer()
		observer.schedule(util.watchdog.GcodeWatchdogHandler(fileManager, printer), self._settings.getBaseFolder("watched"))
		observer.start()

		# run our startup plugins
		octoprint.plugin.call_plugin(octoprint.plugin.StartupPlugin,
		                             "on_startup",
		                             args=(self._host, self._port),
		                             sorting_context="StartupPlugin.on_startup")

		def call_on_startup(name, plugin):
			implementation = plugin.get_implementation(octoprint.plugin.StartupPlugin)
			if implementation is None:
				return
			implementation.on_startup(self._host, self._port)
		pluginLifecycleManager.add_callback("enabled", call_on_startup)

		# prepare our after startup function
		def on_after_startup():
			self._logger.info("Listening on http://%s:%d" % (self._host, self._port))

			if safe_mode and self._settings.getBoolean(["server", "startOnceInSafeMode"]):
				self._logger.info("Server started successfully in safe mode as requested from config, removing flag")
				self._settings.setBoolean(["server", "startOnceInSafeMode"], False)
				self._settings.save()

			# now this is somewhat ugly, but the issue is the following: startup plugins might want to do things for
			# which they need the server to be already alive (e.g. for being able to resolve urls, such as favicons
			# or service xmls or the like). While they are working though the ioloop would block. Therefore we'll
			# create a single use thread in which to perform our after-startup-tasks, start that and hand back
			# control to the ioloop
			def work():
				octoprint.plugin.call_plugin(octoprint.plugin.StartupPlugin,
				                             "on_after_startup",
				                             sorting_context="StartupPlugin.on_after_startup")

				def call_on_after_startup(name, plugin):
					implementation = plugin.get_implementation(octoprint.plugin.StartupPlugin)
					if implementation is None:
						return
					implementation.on_after_startup()
				pluginLifecycleManager.add_callback("enabled", call_on_after_startup)

				# when we are through with that we also run our preemptive cache
				if settings().getBoolean(["devel", "cache", "preemptive"]):
					self._execute_preemptive_flask_caching(preemptiveCache)

			import threading
			threading.Thread(target=work).start()
		ioloop.add_callback(on_after_startup)

		# prepare our shutdown function
		def on_shutdown():
			# will be called on clean system exit and shutdown the watchdog observer and call the on_shutdown methods
			# on all registered ShutdownPlugins
			self._logger.info("Shutting down...")
			observer.stop()
			observer.join()
			eventManager.fire(events.Events.SHUTDOWN)
			octoprint.plugin.call_plugin(octoprint.plugin.ShutdownPlugin,
			                             "on_shutdown",
			                             sorting_context="ShutdownPlugin.on_shutdown")

			# wait for shutdown event to be processed, but maximally for 15s
			event_timeout = 15.0
			if eventManager.join(timeout=event_timeout):
				self._logger.warn("Event loop was still busy processing after {}s, shutting down anyhow".format(event_timeout))

			if self._octoprint_daemon is not None:
				self._logger.info("Cleaning up daemon pidfile")
				self._octoprint_daemon.terminated()

			self._logger.info("Goodbye!")
		atexit.register(on_shutdown)

		def sigterm_handler(*args, **kwargs):
			# will stop tornado on SIGTERM, making the program exit cleanly
			def shutdown_tornado():
				self._logger.debug("Shutting down tornado's IOLoop...")
				ioloop.stop()
			self._logger.debug("SIGTERM received...")
			ioloop.add_callback_from_signal(shutdown_tornado)
		signal.signal(signal.SIGTERM, sigterm_handler)

		try:
			# this is the main loop - as long as tornado is running, OctoPrint is running
			ioloop.start()
			self._logger.debug("Tornado's IOLoop stopped")
		except (KeyboardInterrupt, SystemExit):
			pass
		except:
			self._logger.fatal("Now that is embarrassing... Something really really went wrong here. Please report this including the stacktrace below in OctoPrint's bugtracker. Thanks!")
			self._logger.exception("Stacktrace follows:")