	def run(self):
		if not self._allow_root:
			self._check_for_root()

		if self._settings is None:
			self._settings = settings()

		if not self._settings.getBoolean(["server", "ignoreIncompleteStartup"]):
			self._settings.setBoolean(["server", "incompleteStartup"], True)
			self._settings.save()

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
		global permissionManager
		global groupManager
		global eventManager
		global loginManager
		global pluginManager
		global pluginLifecycleManager
		global preemptiveCache
		global jsonEncoder
		global jsonDecoder
		global connectivityChecker
		global debug
		global safe_mode

		from tornado.ioloop import IOLoop
		from tornado.web import Application

		debug = self._debug
		safe_mode = self._safe_mode

		if self._v6_only and not octoprint.util.net.HAS_V6:
			raise RuntimeError("IPv6 only mode configured but system doesn't support IPv6")

		if self._host is None:
			host = self._settings.get(["server", "host"])
			if host is None:
				if octoprint.util.net.HAS_V6:
					host = "::"
				else:
					host = "0.0.0.0"

			self._host = host

		if ":" in self._host and not octoprint.util.net.HAS_V6:
			raise RuntimeError("IPv6 host address {!r} configured but system doesn't support IPv6".format(self._host))

		if self._port is None:
			self._port = self._settings.getInt(["server", "port"])
			if self._port is None:
				self._port = 5000

		self._logger = logging.getLogger(__name__)
		self._setup_heartbeat_logging()
		pluginManager = self._plugin_manager

		# monkey patch/fix some stuff
		util.tornado.fix_json_encode()
		util.tornado.fix_websocket_check_origin()
		util.flask.fix_flask_jsonify()

		self._setup_mimetypes()

		additional_translation_folders = []
		if not safe_mode:
			additional_translation_folders += [self._settings.getBaseFolder("translations")]
		util.flask.enable_additional_translations(additional_folders=additional_translation_folders)

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
		### we can only do that if fcntl is available or we are on Windows, so better safe than sorry.
		###
		### See also issues #2035 and #2090

		# then initialize the plugin manager
		pluginManager.reload_plugins(startup=True, initialize_implementations=False)

		printerProfileManager = PrinterProfileManager()
		eventManager = self._event_manager

		analysis_queue_factories = dict(gcode=octoprint.filemanager.analysis.GcodeAnalysisQueue)
		analysis_queue_hooks = pluginManager.get_hooks("octoprint.filemanager.analysis.factory")
		for name, hook in analysis_queue_hooks.items():
			try:
				additional_factories = hook()
				analysis_queue_factories.update(**additional_factories)
			except Exception:
				self._logger.exception("Error while processing analysis queues from {}".format(name),
				                       extra=dict(plugin=name))
		analysisQueue = octoprint.filemanager.analysis.AnalysisQueue(analysis_queue_factories)

		slicingManager = octoprint.slicing.SlicingManager(self._settings.getBaseFolder("slicingProfiles"), printerProfileManager)

		storage_managers = dict()
		storage_managers[octoprint.filemanager.FileDestinations.LOCAL] = octoprint.filemanager.storage.LocalFileStorage(self._settings.getBaseFolder("uploads"))

		fileManager = octoprint.filemanager.FileManager(analysisQueue, slicingManager, printerProfileManager, initial_storage_managers=storage_managers)
		pluginLifecycleManager = LifecycleManager(pluginManager)
		preemptiveCache = PreemptiveCache(os.path.join(self._settings.getBaseFolder("data"), "preemptive_cache_config.yaml"))

		JsonEncoding.add_encoder(users.User, lambda obj: obj.as_dict())
		JsonEncoding.add_encoder(groups.Group, lambda obj: obj.as_dict())
		JsonEncoding.add_encoder(permissions.OctoPrintPermission, lambda obj: obj.as_dict())

		# start regular check if we are connected to the internet
		def on_connectivity_change(old_value, new_value):
			eventManager.fire(events.Events.CONNECTIVITY_CHANGED, payload=dict(old=old_value, new=new_value))

		connectivityChecker = self._connectivity_checker

		def on_settings_update(*args, **kwargs):
			# make sure our connectivity checker runs with the latest settings
			connectivityEnabled = self._settings.getBoolean(["server", "onlineCheck", "enabled"])
			connectivityInterval = self._settings.getInt(["server", "onlineCheck", "interval"])
			connectivityHost = self._settings.get(["server", "onlineCheck", "host"])
			connectivityPort = self._settings.getInt(["server", "onlineCheck", "port"])
			connectivityName = self._settings.get(["server", "onlineCheck", "name"])

			if connectivityChecker.enabled != connectivityEnabled \
					or connectivityChecker.interval != connectivityInterval \
					or connectivityChecker.host != connectivityHost \
					or connectivityChecker.port != connectivityPort \
					or connectivityChecker.name != connectivityName:
				connectivityChecker.enabled = connectivityEnabled
				connectivityChecker.interval = connectivityInterval
				connectivityChecker.host = connectivityHost
				connectivityChecker.port = connectivityPort
				connectivityChecker.name = connectivityName
				connectivityChecker.check_immediately()

		eventManager.subscribe(events.Events.SETTINGS_UPDATED, on_settings_update)

		components = dict(
			plugin_manager=pluginManager,
			printer_profile_manager=printerProfileManager,
			event_bus=eventManager,
			analysis_queue=analysisQueue,
			slicing_manager=slicingManager,
			file_manager=fileManager,
			plugin_lifecycle_manager=pluginLifecycleManager,
			preemptive_cache=preemptiveCache,
			json_encoder=jsonEncoder,
			json_decoder=jsonDecoder,
			connectivity_checker=connectivityChecker,
			environment_detector=self._environment_detector
		)

		#~~ setup access control

		# get additional permissions from plugins
		self._setup_plugin_permissions()

		# create group manager instance
		group_manager_factories = pluginManager.get_hooks("octoprint.access.groups.factory")
		for name, factory in group_manager_factories.items():
			try:
				groupManager = factory(components, self._settings)
				if groupManager is not None:
					self._logger.debug("Created group manager instance from factory {}".format(name))
					break
			except Exception:
				self._logger.exception("Error while creating group manager instance from factory {}".format(name))
		else:
			group_manager_name = self._settings.get(["accessControl", "groupManager"])
			try:
				clazz = octoprint.util.get_class(group_manager_name)
				groupManager = clazz()
			except AttributeError:
				self._logger.exception("Could not instantiate group manager {}, "
				                       "falling back to FilebasedGroupManager!".format(group_manager_name))
				groupManager = octoprint.access.groups.FilebasedGroupManager()
		components.update(dict(group_manager=groupManager))

		# create user manager instance
		user_manager_factories = pluginManager.get_hooks("octoprint.users.factory") # legacy, set first so that new wins
		user_manager_factories.update(pluginManager.get_hooks("octoprint.access.users.factory"))
		for name, factory in user_manager_factories.items():
			try:
				userManager = factory(components, self._settings)
				if userManager is not None:
					self._logger.debug("Created user manager instance from factory {}".format(name))
					break
			except Exception:
				self._logger.exception("Error while creating user manager instance from factory {}".format(name),
				                       extra=dict(plugin=name))
		else:
			user_manager_name = self._settings.get(["accessControl", "userManager"])
			try:
				clazz = octoprint.util.get_class(user_manager_name)
				userManager = clazz(groupManager)
			except Exception:
				self._logger.exception("Could not instantiate user manager {}, "
				                       "falling back to FilebasedUserManager!".format(user_manager_name))
				userManager = octoprint.access.users.FilebasedUserManager(groupManager)
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
			except Exception:
				self._logger.exception("Error while creating printer instance from factory {}".format(name),
				                       extra=dict(plugin=name))
		else:
			printer = Printer(fileManager, analysisQueue, printerProfileManager)
		components.update(dict(printer=printer))

		def octoprint_plugin_inject_factory(name, implementation):
			"""Factory for injections for all OctoPrintPlugins"""
			if not isinstance(implementation, octoprint.plugin.OctoPrintPlugin):
				return None

			components_copy = dict(components)
			if "printer" in components:
				import wrapt
				import functools

				def tagwrap(f):
					@functools.wraps(f)
					def wrapper(*args, **kwargs):
						tags = kwargs.get("tags", set()) | {"source:plugin",
						                                    "plugin:{}".format(name)}
						kwargs["tags"] = tags
						return f(*args, **kwargs)
					setattr(wrapper, "__tagwrapped__", True)
					return wrapper

				class TaggedFuncsPrinter(wrapt.ObjectProxy):
					def __getattribute__(self, attr):
						__wrapped__ = super(TaggedFuncsPrinter, self).__getattribute__("__wrapped__")
						if attr == "__wrapped__":
							return __wrapped__

						item = getattr(__wrapped__, attr)
						if callable(item) \
								and ("tags" in item.__code__.co_varnames or "kwargs" in item.__code__.co_varnames) \
								and not getattr(item, "__tagwrapped__", False):
							return tagwrap(item)
						else:
							return item

				components_copy["printer"] = TaggedFuncsPrinter(components["printer"])

			props = dict()
			props.update(components_copy)
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

		custom_events_hooks = pluginManager.get_hooks("octoprint.events.register_custom_events")
		for name, hook in custom_events_hooks.items():
			try:
				result = hook()
				if isinstance(result, (list, tuple)):
					for event in result:
						constant, value = octoprint.events.Events.register_event(event, prefix="plugin_{}_".format(name))
						self._logger.debug("Registered event {} of plugin {} as Events.{} = \"{}\"".format(event, name, constant, value))
			except Exception:
				self._logger.exception("Error while retrieving custom event list from plugin {}".format(name),
				                       extra=dict(plugin=name))

		pluginManager.implementation_inject_factories=[octoprint_plugin_inject_factory,
		                                               settings_plugin_inject_factory]
		pluginManager.initialize_implementations()

		settingsPlugins = pluginManager.get_implementations(octoprint.plugin.SettingsPlugin)
		for implementation in settingsPlugins:
			try:
				settings_plugin_config_migration_and_cleanup(implementation._identifier, implementation)
			except Exception:
				self._logger.exception("Error while trying to migrate settings for "
				                       "plugin {}, ignoring it".format(implementation._identifier),
				                       extra=dict(plugin=implementation._identifier))

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

		# setup assets
		self._setup_assets()

		# configure timelapse
		octoprint.timelapse.valid_timelapse("test")
		octoprint.timelapse.configure_timelapse()

		# setup command triggers
		events.CommandTrigger(printer)
		if self._debug:
			events.DebugEventListener()

		# setup login manager
		self._setup_login_manager()

		# register API blueprint
		self._setup_blueprints()

		## Tornado initialization starts here

		ioloop = IOLoop()
		ioloop.install()

		enable_cors = settings().getBoolean(["api", "allowCrossOrigin"])

		self._router = SockJSRouter(self._create_socket_connection, "/sockjs",
		                            session_kls=util.sockjs.ThreadSafeSession,
		                            user_settings=dict(websocket_allow_origin="*" if enable_cors else "",
		                                               jsessionid=False,
		                                               sockjs_url="../../static/js/lib/sockjs.min.js"))

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

		##~~ Permission validators

		access_validators_from_plugins = []
		for plugin, hook in pluginManager.get_hooks("octoprint.server.http.access_validator").items():
			try:
				access_validators_from_plugins.append(util.tornado.access_validation_factory(app, hook))
			except Exception:
				self._logger.exception("Error while adding tornado access validator from plugin {}".format(plugin),
				                       extra=dict(plugin=plugin))
		access_validator = dict(access_validation=util.tornado.validation_chain(*access_validators_from_plugins))

		timelapse_validators = [util.tornado.access_validation_factory(app, util.flask.permission_validator, permissions.Permissions.TIMELAPSE_LIST),] + access_validators_from_plugins
		download_validators = [util.tornado.access_validation_factory(app, util.flask.permission_validator, permissions.Permissions.FILES_DOWNLOAD),] + access_validators_from_plugins
		log_validators = [util.tornado.access_validation_factory(app, util.flask.permission_validator, permissions.Permissions.PLUGIN_LOGGING_MANAGE),] + access_validators_from_plugins
		camera_validators = [util.tornado.access_validation_factory(app, util.flask.permission_validator, permissions.Permissions.WEBCAM),] + access_validators_from_plugins

		timelapse_permission_validator = dict(access_validation=util.tornado.validation_chain(*timelapse_validators))
		download_permission_validator = dict(access_validation=util.tornado.validation_chain(*download_validators))
		log_permission_validator = dict(access_validation=util.tornado.validation_chain(*log_validators))
		camera_permission_validator = dict(access_validation=util.tornado.validation_chain(*camera_validators))

		no_hidden_files_validator = dict(path_validation=util.tornado.path_validation_factory(lambda path: not octoprint.util.is_hidden_path(path),
		                                                                                      status_code=404))
		timelapse_path_validator = dict(path_validation=util.tornado.path_validation_factory(lambda path: not octoprint.util.is_hidden_path(path) and octoprint.timelapse.valid_timelapse(path),
		                                                                                status_code=404))

		def joined_dict(*dicts):
			if not len(dicts):
				return dict()

			joined = dict()
			for d in dicts:
				joined.update(d)
			return joined

		util.tornado.RequestlessExceptionLoggingMixin.LOG_REQUEST = debug
		util.tornado.CorsSupportMixin.ENABLE_CORS = enable_cors

		server_routes = self._router.urls + [
			# various downloads
			# .mpg and .mp4 timelapses:
			(r"/downloads/timelapse/(.*)", util.tornado.LargeResponseHandler, joined_dict(dict(path=self._settings.getBaseFolder("timelapse")),
			                                                                              timelapse_permission_validator,
			                                                                              download_handler_kwargs,
			                                                                              timelapse_path_validator)),
			(r"/downloads/files/local/(.*)", util.tornado.LargeResponseHandler, joined_dict(dict(path=self._settings.getBaseFolder("uploads"),
			                                                                                     as_attachment=True,
			                                                                                     name_generator=download_name_generator),
			                                                                                download_permission_validator,
			                                                                                download_handler_kwargs,
			                                                                                no_hidden_files_validator,
			                                                                                additional_mime_types)),
			(r"/downloads/logs/([^/]*)", util.tornado.LargeResponseHandler, joined_dict(dict(path=self._settings.getBaseFolder("logs"),
			                                                                                 mime_type_guesser=lambda *args, **kwargs: "text/plain"),
			                                                                            download_handler_kwargs,
			                                                                            log_permission_validator)),
			# camera snapshot
			(r"/downloads/camera/current", util.tornado.UrlProxyHandler, joined_dict(dict(url=self._settings.get(["webcam", "snapshot"]),
			                                                                              as_attachment=True),
			                                                                         camera_permission_validator)),
			# generated webassets
			(r"/static/webassets/(.*)", util.tornado.LargeResponseHandler, dict(path=os.path.join(self._settings.getBaseFolder("generated"), "webassets"),
			                                                                    is_pre_compressed=True)),

			# online indicators - text file with "online" as content and a transparent gif
			(r"/online.txt", util.tornado.StaticDataHandler, dict(data="online\n")),
			(r"/online.gif", util.tornado.StaticDataHandler, dict(data=bytes(base64.b64decode("R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7")),
			                                                      content_type="image/gif")),

			# deprecated endpoints
			(r"/api/logs", util.tornado.DeprecatedEndpointHandler, dict(url="/plugin/logging/logs")),
			(r"/api/logs/(.*)", util.tornado.DeprecatedEndpointHandler, dict(url="/plugin/logging/logs/{0}")),
		]

		# fetch additional routes from plugins
		for name, hook in pluginManager.get_hooks("octoprint.server.http.routes").items():
			try:
				result = hook(list(server_routes))
			except Exception:
				self._logger.exception("There was an error while retrieving additional "
				                       "server routes from plugin hook {name}".format(**locals()),
				                       extra=dict(plugin=name))
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

		headers =         {"X-Robots-Tag": "noindex, nofollow, noimageindex",
		                   "X-Content-Type-Options": "nosniff"}
		if not settings().getBoolean(["server", "allowFraming"]):
			headers["X-Frame-Options"] = "sameorigin"

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
			except Exception:
				self._logger.exception("There was an error while retrieving additional "
				                       "upload sizes from plugin hook {name}".format(**locals()),
				                       extra=dict(plugin=name))
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
		trusted_downstream = self._settings.get(["server", "reverseProxy", "trustedDownstream"])
		if not isinstance(trusted_downstream, list):
			self._logger.warning("server.reverseProxy.trustedDownstream is not a list, skipping")
			trusted_downstreams = []

		server_kwargs = dict(max_body_sizes=max_body_sizes,
		                     default_max_body_size=self._settings.getInt(["server", "maxSize"]),
		                     xheaders=True,
		                     trusted_downstream=trusted_downstream)
		if sys.platform == "win32":
			# set 10min idle timeout under windows to hopefully make #2916 less likely
			server_kwargs.update(dict(idle_connection_timeout=600))

		self._server = util.tornado.CustomHTTPServer(self._tornado_app, **server_kwargs)

		listening_address = self._host
		if self._host == "::" and not self._v6_only:
			# special case - tornado only listens on v4 _and_ v6 if we use None as address
			listening_address = None

		self._server.listen(self._port, address=listening_address)

		### From now on it's ok to launch subprocesses again

		eventManager.fire(events.Events.STARTUP)

		# analysis backlog
		fileManager.process_backlog()

		# auto connect
		if self._settings.getBoolean(["serial", "autoconnect"]):
			self._logger.info("Autoconnect on startup is configured, trying to connect to the printer...")
			try:
				(port, baudrate) = self._settings.get(["serial", "port"]), self._settings.getInt(["serial", "baudrate"])
				printer_profile = printerProfileManager.get_default()
				connectionOptions = printer.__class__.get_connection_options()
				if port in connectionOptions["ports"] or port == "AUTO" or port is None:
					self._logger.info("Trying to connect to configured serial port {}".format(port))
					printer.connect(port=port, baudrate=baudrate, profile=printer_profile["id"] if "id" in printer_profile else "_default")
				else:
					self._logger.info("Could not find configured serial port {} in the system, cannot automatically connect to a non existing printer. Is it plugged in and booted up yet?")
			except Exception:
				self._logger.exception("Something went wrong while attempting to automatically connect to the printer")

		# start up watchdogs
		try:
			watched = self._settings.getBaseFolder("watched")
			watchdog_handler = util.watchdog.GcodeWatchdogHandler(fileManager, printer)
			watchdog_handler.initial_scan(watched)

			if self._settings.getBoolean(["feature", "pollWatched"]):
				# use less performant polling observer if explicitly configured
				observer = PollingObserver()
			else:
				# use os default
				observer = Observer()

			observer.schedule(watchdog_handler, watched, recursive=True)
			observer.start()
		except Exception:
			self._logger.exception("Error starting watched folder observer")

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
			if self._host == "::":
				if self._v6_only:
					# only v6
					self._logger.info("Listening on http://[::]:{port}".format(port=self._port))
				else:
					# all v4 and v6
					self._logger.info("Listening on http://0.0.0.0:{port} and http://[::]:{port}".format(port=self._port))
			else:
				self._logger.info("Listening on http://{}:{}".format(self._host if not ":" in self._host else "[" + self._host + "]",
				                                                     self._port))

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

				# if there was a rogue plugin we wouldn't even have made it here, so remove startup triggered safe mode
				# flag again...
				self._settings.setBoolean(["server", "incompleteStartup"], False)
				self._settings.save()

				# make a backup of the current config
				self._settings.backup(ext="backup")

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

			self._logger.info("Calling on_shutdown on plugins")
			octoprint.plugin.call_plugin(octoprint.plugin.ShutdownPlugin,
			                             "on_shutdown",
			                             sorting_context="ShutdownPlugin.on_shutdown")

			# wait for shutdown event to be processed, but maximally for 15s
			event_timeout = 15.0
			if eventManager.join(timeout=event_timeout):
				self._logger.warning("Event loop was still busy processing after {}s, shutting down anyhow".format(event_timeout))

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
		except Exception:
			self._logger.fatal("Now that is embarrassing... Something really really went wrong here. Please report this including the stacktrace below in OctoPrint's bugtracker. Thanks!")
			self._logger.exception("Stacktrace follows:")