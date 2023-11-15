	def process_blacklist(entries):
		result = []

		if not isinstance(entries, list):
			return result

		for entry in entries:
			if not "plugin" in entry:
				continue

			if "octoversions" in entry and not is_octoprint_compatible(*entry["octoversions"]):
				continue

			if "version" in entry:
				logger.debug("Blacklisted plugin: {}, version: {}".format(entry["plugin"], entry["version"]))
				result.append((entry["plugin"], entry["version"]))
			elif "versions" in entry:
				logger.debug("Blacklisted plugin: {}, versions: {}".format(entry["plugin"], ", ".join(entry["versions"])))
				for version in entry["versions"]:
					result.append((entry["plugin"], version))
			else:
				logger.debug("Blacklisted plugin: {}".format(entry["plugin"]))
				result.append(entry["plugin"])

		return result