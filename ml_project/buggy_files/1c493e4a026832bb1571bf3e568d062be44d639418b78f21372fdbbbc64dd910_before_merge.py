def _getAvailableAddonsFromPath(path):
	""" Gets available add-ons from path.
	An addon is only considered available if the manifest file is loaded with no errors.
	@param path: path from where to find addon directories.
	@type path: string
	@rtype generator of Addon instances
	"""
	log.debug("Listing add-ons from %s", path)
	for p in os.listdir(path):
		if p.endswith(DELETEDIR_SUFFIX): continue
		addon_path = os.path.join(path, p)
		if os.path.isdir(addon_path) and addon_path not in ('.', '..'):
			log.debug("Loading add-on from %s", addon_path)
			try:
				a = Addon(addon_path)
				name = a.manifest['name']
				log.debug(
					"Found add-on {name} - {a.version}."
					" Requires API: {a.minimumNVDAVersion}."
					" Last-tested API: {a.lastTestedNVDAVersion}".format(
						name=name,
						a=a
					))
				if a.isDisabled:
					log.debug("Disabling add-on %s", name)
				if not isAddonCompatible(a):
					log.debugWarning("Add-on %s is considered incompatible", name)
					_blockedAddons.add(a.name)
				yield a
			except:
				log.error("Error loading Addon from path: %s", addon_path, exc_info=True)