	def _find_plugins_from_entry_points(self, groups, existing, ignore_uninstalled=True):
		result = OrderedDict()

		# let's make sure we have a current working set ...
		working_set = pkg_resources.WorkingSet()

		# ... including the user's site packages
		import site
		import sys
		if site.ENABLE_USER_SITE:
			if not site.USER_SITE in working_set.entries:
				working_set.add_entry(site.USER_SITE)
			if not site.USER_SITE in sys.path:
				site.addsitedir(site.USER_SITE)

		if not isinstance(groups, (list, tuple)):
			groups = [groups]

		def wrapped(gen):
			# to protect against some issues in installed packages that make iteration over entry points
			# fall on its face - e.g. https://groups.google.com/forum/#!msg/octoprint/DyXdqhR0U7c/kKMUsMmIBgAJ
			for entry in gen:
				try:
					yield entry
				except:
					self.logger.exception("Something went wrong while processing the entry points of a package in the "
					                      "Python environment - broken entry_points.txt in some package?")

		for group in groups:
			for entry_point in wrapped(working_set.iter_entry_points(group=group, name=None)):
				try:
					key = entry_point.name
					module_name = entry_point.module_name
					version = entry_point.dist.version

					if key in existing or key in result or (ignore_uninstalled and key in self.marked_plugins["uninstalled"]):
						# plugin is already defined or marked as uninstalled, ignore it
						continue

					kwargs = dict(module_name=module_name, version=version)
					package_name = None
					try:
						module_pkginfo = InstalledEntryPoint(entry_point)
					except:
						self.logger.exception("Something went wrong while retrieving package info data for module %s" % module_name)
					else:
						kwargs.update(dict(
							name=module_pkginfo.name,
							summary=module_pkginfo.summary,
							author=module_pkginfo.author,
							url=module_pkginfo.home_page,
							license=module_pkginfo.license
						))
						package_name = module_pkginfo.name

					plugin = self._import_plugin_from_module(key, **kwargs)
					if plugin:
						plugin.origin = EntryPointOrigin("entry_point", group, module_name, package_name, version)
						plugin.enabled = False

						# plugin is manageable if its location is writable and OctoPrint
						# is either not running from a virtual env or the plugin is
						# installed in that virtual env - the virtual env's pip will not
						# allow us to uninstall stuff that is installed outside
						# of the virtual env, so this check is necessary
						plugin.managable = os.access(plugin.location, os.W_OK) \
						                   and (not self._python_virtual_env
						                        or is_sub_path_of(plugin.location, self._python_prefix)
						                        or is_editable_install(self._python_install_dir,
						                                               package_name,
						                                               module_name,
						                                               plugin.location))

						result[key] = plugin
				except:
					self.logger.exception("Error processing entry point {!r} for group {}".format(entry_point, group))

		return result