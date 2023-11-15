def fetch_template_data(refresh=False):
	global _templates, _plugin_names, _plugin_vars

	locale = g.locale.language if g.locale else "en"

	if not refresh and _templates.get(locale) is not None and _plugin_names is not None and _plugin_vars is not None:
		return _templates[locale], _plugin_names, _plugin_vars

	first_run = settings().getBoolean(["server", "firstRun"])

	##~~ prepare templates

	templates = defaultdict(lambda: dict(order=[], entries=dict()))

	# rules for transforming template configs to template entries
	template_rules = dict(
		navbar=dict(div=lambda x: "navbar_plugin_" + x, template=lambda x: x + "_navbar.jinja2", to_entry=lambda data: data),
		sidebar=dict(div=lambda x: "sidebar_plugin_" + x, template=lambda x: x + "_sidebar.jinja2", to_entry=lambda data: (data["name"], data)),
		tab=dict(div=lambda x: "tab_plugin_" + x, template=lambda x: x + "_tab.jinja2", to_entry=lambda data: (data["name"], data)),
		settings=dict(div=lambda x: "settings_plugin_" + x, template=lambda x: x + "_settings.jinja2", to_entry=lambda data: (data["name"], data)),
		usersettings=dict(div=lambda x: "usersettings_plugin_" + x, template=lambda x: x + "_usersettings.jinja2", to_entry=lambda data: (data["name"], data)),
		wizard=dict(div=lambda x: "wizard_plugin_" + x, template=lambda x: x + "_wizard.jinja2", to_entry=lambda data: (data["name"], data)),
		about=dict(div=lambda x: "about_plugin_" + x, template=lambda x: x + "_about.jinja2", to_entry=lambda data: (data["name"], data)),
		generic=dict(template=lambda x: x + ".jinja2", to_entry=lambda data: data)
	)

	# sorting orders
	def wizard_key_extractor(d, k):
		if d[1].get("_key", None) == "plugin_corewizard_acl":
			# Ultra special case - we MUST always have the ACL wizard first since otherwise any steps that follow and
			# that require to access APIs to function will run into errors since those APIs won't work before ACL
			# has been configured. See also #2140
			return "0:{}".format(to_unicode(d[0]))
		elif d[1].get("mandatory", False):
			# Other mandatory steps come before the optional ones
			return "1:{}".format(to_unicode(d[0]))
		else:
			# Finally everything else
			return "2:{}".format(to_unicode(d[0]))

	template_sorting = dict(
		navbar=dict(add="prepend", key=None),
		sidebar=dict(add="append", key="name"),
		tab=dict(add="append", key="name"),
		settings=dict(add="custom_append", key="name", custom_add_entries=lambda missing: dict(section_plugins=(gettext("Plugins"), None)), custom_add_order=lambda missing: ["section_plugins"] + missing),
		usersettings=dict(add="append", key="name"),
		wizard=dict(add="append", key="name", key_extractor=wizard_key_extractor),
		about=dict(add="append", key="name"),
		generic=dict(add="append", key=None)
	)

	hooks = pluginManager.get_hooks("octoprint.ui.web.templatetypes")
	for name, hook in hooks.items():
		try:
			result = hook(dict(template_sorting), dict(template_rules))
		except Exception:
			_logger.exception("Error while retrieving custom template type "
			                  "definitions from plugin {name}".format(**locals()),
			                  extra=dict(plugin=name))
		else:
			if not isinstance(result, list):
				continue

			for entry in result:
				if not isinstance(entry, tuple) or not len(entry) == 3:
					continue

				key, order, rule = entry

				# order defaults
				if "add" not in order:
					order["add"] = "prepend"
				if "key" not in order:
					order["key"] = "name"

				# rule defaults
				if "div" not in rule:
					# default div name: <hook plugin>_<template_key>_plugin_<plugin>
					div = "{name}_{key}_plugin_".format(**locals())
					rule["div"] = lambda x: div + x
				if "template" not in rule:
					# default template name: <plugin>_plugin_<hook plugin>_<template key>.jinja2
					template = "_plugin_{name}_{key}.jinja2".format(**locals())
					rule["template"] = lambda x: x + template
				if "to_entry" not in rule:
					# default to_entry assumes existing "name" property to be used as label for 2-tuple entry data structure (<name>, <properties>)
					rule["to_entry"] = lambda data: (data["name"], data)

				template_rules["plugin_" + name + "_" + key] = rule
				template_sorting["plugin_" + name + "_" + key] = order
	template_types = list(template_rules.keys())

	# navbar

	templates["navbar"]["entries"] = dict(
		settings=dict(template="navbar/settings.jinja2", _div="navbar_settings", styles=["display: none;"], data_bind="visible: loginState.hasPermissionKo(access.permissions.SETTINGS)"),
		systemmenu=dict(template="navbar/systemmenu.jinja2", _div="navbar_systemmenu", classes=["dropdown"], styles=["display: none;"], data_bind="visible: loginState.hasPermissionKo(access.permissions.SYSTEM)", custom_bindings=False),
		login=dict(template="navbar/login.jinja2", _div="navbar_login", classes=["dropdown"], custom_bindings=False),
	)

	# sidebar

	templates["sidebar"]["entries"]= dict(
		connection=(gettext("Connection"), dict(template="sidebar/connection.jinja2", _div="connection", icon="signal", styles_wrapper=["display: none;"], data_bind="visible: loginState.hasPermissionKo(access.permissions.CONNECTION)", template_header="sidebar/connection_header.jinja2")),
		state=(gettext("State"), dict(template="sidebar/state.jinja2", _div="state", icon="info-circle", styles_wrapper=["display: none;"], data_bind="visible: loginState.hasPermissionKo(access.permissions.STATUS)")),
		files=(gettext("Files"), dict(template="sidebar/files.jinja2", _div="files", icon="list", classes_content=["overflow_visible"], template_header="sidebar/files_header.jinja2", styles_wrapper=["display: none;"], data_bind="visible: loginState.hasPermissionKo(access.permissions.FILES_LIST)"))
	)

	# tabs

	templates["tab"]["entries"] = dict(
		temperature=(gettext("Temperature"), dict(template="tabs/temperature.jinja2", _div="temp", styles=["display: none;"], data_bind="visible: loginState.hasAnyPermissionKo(access.permissions.STATUS, access.permissions.CONTROL) && visible()")),
		control=(gettext("Control"), dict(template="tabs/control.jinja2", _div="control", styles=["display: none;"], data_bind="visible: loginState.hasAnyPermissionKo(access.permissions.WEBCAM, access.permissions.CONTROL)")),
		gcodeviewer=(gettext("GCode Viewer"), dict(template="tabs/gcodeviewer.jinja2", _div="gcode", styles=["display: none;"], data_bind="visible: loginState.hasPermissionKo(access.permissions.GCODE_VIEWER)")),
		terminal=(gettext("Terminal"), dict(template="tabs/terminal.jinja2", _div="term", styles=["display: none;"], data_bind="visible: loginState.hasPermissionKo(access.permissions.MONITOR_TERMINAL)")),
		timelapse=(gettext("Timelapse"), dict(template="tabs/timelapse.jinja2", _div="timelapse", styles=["display: none;"], data_bind="visible: loginState.hasPermissionKo(access.permissions.TIMELAPSE_LIST)"))
	)

	# settings dialog

	templates["settings"]["entries"] = dict(
		section_printer=(gettext("Printer"), None),

		serial=(gettext("Serial Connection"), dict(template="dialogs/settings/serialconnection.jinja2", _div="settings_serialConnection", custom_bindings=False)),
		printerprofiles=(gettext("Printer Profiles"), dict(template="dialogs/settings/printerprofiles.jinja2", _div="settings_printerProfiles", custom_bindings=False)),
		temperatures=(gettext("Temperatures"), dict(template="dialogs/settings/temperatures.jinja2", _div="settings_temperature", custom_bindings=False)),
		terminalfilters=(gettext("Terminal Filters"), dict(template="dialogs/settings/terminalfilters.jinja2", _div="settings_terminalFilters", custom_bindings=False)),
		gcodescripts=(gettext("GCODE Scripts"), dict(template="dialogs/settings/gcodescripts.jinja2", _div="settings_gcodeScripts", custom_bindings=False)),

		section_features=(gettext("Features"), None),

		features=(gettext("Features"), dict(template="dialogs/settings/features.jinja2", _div="settings_features", custom_bindings=False)),
		webcam=(gettext("Webcam & Timelapse"), dict(template="dialogs/settings/webcam.jinja2", _div="settings_webcam", custom_bindings=False)),
		gcodevisualizer=(gettext("GCODE Visualizer"), dict(template="dialogs/settings/gcodevisualizer.jinja2", _div="settings_gcodegcodevisualizer", custom_bindings=False)),
		api=(gettext("API"), dict(template="dialogs/settings/api.jinja2", _div="settings_api", custom_bindings=False)),

		section_octoprint=(gettext("OctoPrint"), None),

		accesscontrol=(gettext("Access Control"), dict(template="dialogs/settings/accesscontrol.jinja2", _div="settings_users", custom_bindings=False)),
		folders=(gettext("Folders"), dict(template="dialogs/settings/folders.jinja2", _div="settings_folders", custom_bindings=False)),
		appearance=(gettext("Appearance"), dict(template="dialogs/settings/appearance.jinja2", _div="settings_appearance", custom_bindings=False)),
		server=(gettext("Server"), dict(template="dialogs/settings/server.jinja2", _div="settings_server", custom_bindings=False)),
	)

	# user settings dialog

	templates["usersettings"]["entries"] = dict(
		access=(gettext("Access"), dict(template="dialogs/usersettings/access.jinja2", _div="usersettings_access", custom_bindings=False)),
		interface=(gettext("Interface"), dict(template="dialogs/usersettings/interface.jinja2", _div="usersettings_interface", custom_bindings=False)),
	)

	# wizard

	if first_run:
		def custom_insert_order(existing, missing):
			if "firstrunstart" in missing:
				missing.remove("firstrunstart")
			if "firstrunend" in missing:
				missing.remove("firstrunend")

			return ["firstrunstart"] + existing + missing + ["firstrunend"]

		template_sorting["wizard"].update(dict(add="custom_insert", custom_insert_entries=lambda missing: dict(), custom_insert_order=custom_insert_order))
		templates["wizard"]["entries"] = dict(
			firstrunstart=(gettext("Start"), dict(template="dialogs/wizard/firstrun_start.jinja2", _div="wizard_firstrun_start")),
			firstrunend=(gettext("Finish"), dict(template="dialogs/wizard/firstrun_end.jinja2", _div="wizard_firstrun_end")),
		)

	# about dialog

	templates["about"]["entries"] = dict(
		about=("About OctoPrint", dict(template="dialogs/about/about.jinja2", _div="about_about", custom_bindings=False)),
		license=("OctoPrint License", dict(template="dialogs/about/license.jinja2", _div="about_license", custom_bindings=False)),
		thirdparty=("Third Party Licenses", dict(template="dialogs/about/thirdparty.jinja2", _div="about_thirdparty", custom_bindings=False)),
		authors=("Authors", dict(template="dialogs/about/authors.jinja2", _div="about_authors", custom_bindings=False)),
		changelog=("Changelog", dict(template="dialogs/about/changelog.jinja2", _div="about_changelog", custom_bindings=False)),
		supporters=("Supporters", dict(template="dialogs/about/supporters.jinja2", _div="about_sponsors", custom_bindings=False))
	)

	# extract data from template plugins

	template_plugins = pluginManager.get_implementations(octoprint.plugin.TemplatePlugin)

	plugin_vars = dict()
	plugin_names = set()
	seen_wizards = settings().get(["server", "seenWizards"]) if not first_run else dict()
	for implementation in template_plugins:
		name = implementation._identifier
		plugin_names.add(name)
		wizard_required = False
		wizard_ignored = False

		try:
			vars = implementation.get_template_vars()
			configs = implementation.get_template_configs()
			if isinstance(implementation, octoprint.plugin.WizardPlugin):
				wizard_required = implementation.is_wizard_required()
				wizard_ignored = octoprint.plugin.WizardPlugin.is_wizard_ignored(seen_wizards, implementation)
		except Exception:
			_logger.exception("Error while retrieving template data for plugin {}, ignoring it".format(name),
			                  extra=dict(plugin=name))
			continue

		if not isinstance(vars, dict):
			vars = dict()
		if not isinstance(configs, (list, tuple)):
			configs = []

		for var_name, var_value in vars.items():
			plugin_vars["plugin_" + name + "_" + var_name] = var_value

		includes = _process_template_configs(name, implementation, configs, template_rules)

		if not wizard_required or wizard_ignored:
			includes["wizard"] = list()

		for t in template_types:
			for include in includes[t]:
				if t == "navbar" or t == "generic":
					data = include
				else:
					data = include[1]

				key = data["_key"]
				if "replaces" in data:
					key = data["replaces"]
				templates[t]["entries"][key] = include

	#~~ order internal templates and plugins

	# make sure that
	# 1) we only have keys in our ordered list that we have entries for and
	# 2) we have all entries located somewhere within the order

	for t in template_types:
		default_order = settings().get(["appearance", "components", "order", t], merged=True, config=dict()) or []
		configured_order = settings().get(["appearance", "components", "order", t], merged=True) or []
		configured_disabled = settings().get(["appearance", "components", "disabled", t]) or []

		# first create the ordered list of all component ids according to the configured order
		templates[t]["order"] = [x for x in configured_order if x in templates[t]["entries"] and not x in configured_disabled]

		# now append the entries from the default order that are not already in there
		templates[t]["order"] += [x for x in default_order if not x in templates[t]["order"] and x in templates[t]["entries"] and not x in configured_disabled]

		all_ordered = set(templates[t]["order"])
		all_disabled = set(configured_disabled)

		# check if anything is missing, if not we are done here
		missing_in_order = set(templates[t]["entries"].keys()).difference(all_ordered).difference(all_disabled)
		if len(missing_in_order) == 0:
			continue

		# works with entries that are dicts and entries that are 2-tuples with the
		# entry data at index 1
		def config_extractor(item, key, default_value=None):
			if isinstance(item, dict) and key in item:
				return item[key] if key in item else default_value
			elif isinstance(item, tuple) and len(item) > 1 and isinstance(item[1], dict) and key in item[1]:
				return item[1][key] if key in item[1] else default_value

			return default_value

		# finally add anything that's not included in our order yet
		if template_sorting[t]["key"] is not None:
			# we'll use our config extractor as default key extractor
			extractor = config_extractor

			# if template type provides custom extractor, make sure its exceptions are handled
			if "key_extractor" in template_sorting[t] and callable(template_sorting[t]["key_extractor"]):
				def create_safe_extractor(extractor):
					def f(x, k):
						try:
							return extractor(x, k)
						except Exception:
							_logger.exception("Error while extracting sorting keys for template {}".format(t))
							return None
					return f
				extractor = create_safe_extractor(template_sorting[t]["key_extractor"])

			sort_key = template_sorting[t]["key"]

			def key_func(x):
				config = templates[t]["entries"][x]
				entry_order = config_extractor(config, "order", default_value=None)
				return entry_order is None, entry_order, extractor(config, sort_key)

			sorted_missing = sorted(missing_in_order, key=key_func)
		else:
			def key_func(x):
				config = templates[t]["entries"][x]
				entry_order = config_extractor(config, "order", default_value=None)
				return entry_order is None, entry_order

			sorted_missing = sorted(missing_in_order, key=key_func)

		if template_sorting[t]["add"] == "prepend":
			templates[t]["order"] = sorted_missing + templates[t]["order"]
		elif template_sorting[t]["add"] == "append":
			templates[t]["order"] += sorted_missing
		elif template_sorting[t]["add"] == "custom_prepend" and "custom_add_entries" in template_sorting[t] and "custom_add_order" in template_sorting[t]:
			templates[t]["entries"].update(template_sorting[t]["custom_add_entries"](sorted_missing))
			templates[t]["order"] = template_sorting[t]["custom_add_order"](sorted_missing) + templates[t]["order"]
		elif template_sorting[t]["add"] == "custom_append" and "custom_add_entries" in template_sorting[t] and "custom_add_order" in template_sorting[t]:
			templates[t]["entries"].update(template_sorting[t]["custom_add_entries"](sorted_missing))
			templates[t]["order"] += template_sorting[t]["custom_add_order"](sorted_missing)
		elif template_sorting[t]["add"] == "custom_insert" and "custom_insert_entries" in template_sorting[t] and "custom_insert_order" in template_sorting[t]:
			templates[t]["entries"].update(template_sorting[t]["custom_insert_entries"](sorted_missing))
			templates[t]["order"] = template_sorting[t]["custom_insert_order"](templates[t]["order"], sorted_missing)

	_templates[locale] = templates
	_plugin_names = plugin_names
	_plugin_vars = plugin_vars

	return templates, plugin_names, plugin_vars