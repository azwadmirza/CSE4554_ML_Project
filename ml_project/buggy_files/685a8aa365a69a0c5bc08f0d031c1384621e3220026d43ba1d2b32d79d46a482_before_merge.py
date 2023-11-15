def index():
	global _templates, _plugin_names, _plugin_vars

	preemptive_cache_enabled = settings().getBoolean(["devel", "cache", "preemptive"])

	locale = g.locale.language if g.locale else "en"

	# helper to check if wizards are active
	def wizard_active(templates):
		return templates is not None and bool(templates["wizard"]["order"])

	# we force a refresh if the client forces one or if we have wizards cached
	force_refresh = util.flask.cache_check_headers() or "_refresh" in request.values or wizard_active(_templates.get(locale))

	# if we need to refresh our template cache or it's not yet set, process it
	fetch_template_data(refresh=force_refresh)

	now = datetime.datetime.utcnow()

	enable_accesscontrol = userManager.enabled
	enable_gcodeviewer = settings().getBoolean(["gcodeViewer", "enabled"])
	enable_timelapse = settings().getBoolean(["webcam", "timelapseEnabled"])

	def default_template_filter(template_type, template_key):
		if template_type == "navbar":
			return template_key != "login" or enable_accesscontrol
		elif template_type == "tab":
			return (template_key != "gcodeviewer" or enable_gcodeviewer) and \
			       (template_key != "timelapse" or enable_timelapse)
		elif template_type == "settings":
			return template_key != "accesscontrol" or enable_accesscontrol
		elif template_type == "usersettings":
			return enable_accesscontrol
		else:
			return True

	default_additional_etag = [enable_accesscontrol,
	                           enable_gcodeviewer,
	                           enable_timelapse] + sorted(["{}:{}".format(k, v) for k, v in _plugin_vars.items()])

	def get_preemptively_cached_view(key, view, data=None, additional_request_data=None, additional_unless=None):
		if (data is None and additional_request_data is None) or g.locale is None:
			return view

		d = _preemptive_data(key, data=data, additional_request_data=additional_request_data)

		def unless():
			return _preemptive_unless(base_url=request.url_root, additional_unless=additional_unless)

		# finally decorate our view
		return util.flask.preemptively_cached(cache=preemptiveCache,
		                                      data=d,
		                                      unless=unless)(view)

	def get_cached_view(key, view, additional_key_data=None, additional_files=None, additional_etag=None, custom_files=None, custom_etag=None, custom_lastmodified=None):
		if additional_etag is None:
			additional_etag = []

		def cache_key():
			return _cache_key(key, additional_key_data=additional_key_data)

		def check_etag_and_lastmodified():
			files = collect_files()
			lastmodified = compute_lastmodified(files)
			lastmodified_ok = util.flask.check_lastmodified(lastmodified)
			etag_ok = util.flask.check_etag(compute_etag(files=files,
			                                             lastmodified=lastmodified,
			                                             additional=[cache_key()] + additional_etag))
			return lastmodified_ok and etag_ok

		def validate_cache(cached):
			etag_different = compute_etag(additional=[cache_key()] + additional_etag) != cached.get_etag()[0]
			return force_refresh or etag_different

		def collect_files():
			if callable(custom_files):
				try:
					files = custom_files()
					if files:
						return files
				except:
					_logger.exception("Error while trying to retrieve tracked files for plugin {}".format(key))

			templates = _get_all_templates()
			assets = _get_all_assets()
			translations = _get_all_translationfiles(g.locale.language if g.locale else "en",
			                                         "messages")

			files = templates + assets + translations

			if callable(additional_files):
				try:
					af = additional_files()
					if af:
						files += af
				except:
					_logger.exception("Error while trying to retrieve additional tracked files for plugin {}".format(key))

			return sorted(set(files))

		def compute_lastmodified(files=None):
			if callable(custom_lastmodified):
				try:
					lastmodified = custom_lastmodified()
					if lastmodified:
						return lastmodified
				except:
					_logger.exception("Error while trying to retrieve custom LastModified value for plugin {}".format(key))

			if files is None:
				files = collect_files()
			return _compute_date(files)

		def compute_etag(files=None, lastmodified=None, additional=None):
			if callable(custom_etag):
				try:
					etag = custom_etag()
					if etag:
						return etag
				except:
					_logger.exception("Error while trying to retrieve custom ETag value for plugin {}".format(key))

			if files is None:
				files = collect_files()
			if lastmodified is None:
				lastmodified = compute_lastmodified(files)
			if lastmodified and not isinstance(lastmodified, basestring):
				from werkzeug.http import http_date
				lastmodified = http_date(lastmodified)
			if additional is None:
				additional = []

			import hashlib
			hash = hashlib.sha1()
			hash.update(octoprint.__version__)
			hash.update(",".join(sorted(files)))
			if lastmodified:
				hash.update(lastmodified)
			for add in additional:
				hash.update(str(add))
			return hash.hexdigest()

		decorated_view = view
		decorated_view = util.flask.lastmodified(lambda _: compute_lastmodified())(decorated_view)
		decorated_view = util.flask.etagged(lambda _: compute_etag(additional=[cache_key()] + additional_etag))(decorated_view)
		decorated_view = util.flask.cached(timeout=-1,
		                                   refreshif=validate_cache,
		                                   key=cache_key,
		                                   unless_response=lambda response: util.flask.cache_check_response_headers(response) or util.flask.cache_check_status_code(response, _valid_status_for_cache))(decorated_view)
		decorated_view = util.flask.with_client_revalidation(decorated_view)
		decorated_view = util.flask.conditional(check_etag_and_lastmodified, NOT_MODIFIED)(decorated_view)
		return decorated_view

	def plugin_view(p):
		cached = get_cached_view(p._identifier,
		                         p.on_ui_render,
		                         additional_key_data=p.get_ui_additional_key_data_for_cache,
		                         additional_files=p.get_ui_additional_tracked_files,
		                         custom_files=p.get_ui_custom_tracked_files,
		                         custom_etag=p.get_ui_custom_etag,
		                         custom_lastmodified=p.get_ui_custom_lastmodified,
		                         additional_etag=p.get_ui_additional_etag(default_additional_etag))

		if preemptive_cache_enabled and p.get_ui_preemptive_caching_enabled():
			view = get_preemptively_cached_view(p._identifier,
			                                    cached,
			                                    p.get_ui_data_for_preemptive_caching,
			                                    p.get_ui_additional_request_data_for_preemptive_caching,
			                                    p.get_ui_preemptive_caching_additional_unless)
		else:
			view = cached

		template_filter = p.get_ui_custom_template_filter(default_template_filter)
		if template_filter is not None and callable(template_filter):
			filtered_templates = _filter_templates(_templates[locale], template_filter)
		else:
			filtered_templates = _templates[locale]

		render_kwargs = _get_render_kwargs(filtered_templates,
		                                   _plugin_names,
		                                   _plugin_vars,
		                                   now)

		return view(now, request, render_kwargs)

	def default_view():
		filtered_templates = _filter_templates(_templates[locale], default_template_filter)

		wizard = wizard_active(filtered_templates)
		accesscontrol_active = enable_accesscontrol and userManager.hasBeenCustomized()

		render_kwargs = _get_render_kwargs(filtered_templates,
		                                   _plugin_names,
		                                   _plugin_vars,
		                                   now)

		render_kwargs.update(dict(
			enableWebcam=settings().getBoolean(["webcam", "webcamEnabled"]) and bool(settings().get(["webcam", "stream"])),
			enableTemperatureGraph=settings().get(["feature", "temperatureGraph"]),
			enableAccessControl=enable_accesscontrol,
			accessControlActive=accesscontrol_active,
			enableSdSupport=settings().get(["feature", "sdSupport"]),
			gcodeMobileThreshold=settings().get(["gcodeViewer", "mobileSizeThreshold"]),
			gcodeThreshold=settings().get(["gcodeViewer", "sizeThreshold"]),
			wizard=wizard,
			now=now,
		))

		# no plugin took an interest, we'll use the default UI
		def make_default_ui():
			r = make_response(render_template("index.jinja2", **render_kwargs))
			if wizard:
				# if we have active wizard dialogs, set non caching headers
				r = util.flask.add_non_caching_response_headers(r)
			return r

		cached = get_cached_view("_default",
		                         make_default_ui,
		                         additional_etag=default_additional_etag)
		preemptively_cached = get_preemptively_cached_view("_default",
		                                                   cached,
		                                                   dict(),
		                                                   dict())
		return preemptively_cached()

	response = None

	forced_view = request.headers.get("X-Force-View", None)

	if forced_view:
		# we have view forced by the preemptive cache
		_logger.debug("Forcing rendering of view {}".format(forced_view))
		if forced_view != "_default":
			plugin = pluginManager.get_plugin_info(forced_view, require_enabled=True)
			if plugin is not None and isinstance(plugin.implementation, octoprint.plugin.UiPlugin):
				response = plugin_view(plugin.implementation)
		else:
			response = default_view()

	else:
		# select view from plugins and fall back on default view if no plugin will handle it
		ui_plugins = pluginManager.get_implementations(octoprint.plugin.UiPlugin, sorting_context="UiPlugin.on_ui_render")
		for plugin in ui_plugins:
			if plugin.will_handle_ui(request):
				# plugin claims responsibility, let it render the UI
				response = plugin_view(plugin)
				if response is not None:
					break
				else:
					_logger.warn("UiPlugin {} returned an empty response".format(plugin._identifier))
		else:
			response = default_view()

	if response is None:
		return abort(404)
	return response