def get_plugin_blacklist(settings, connectivity_checker=None):
	import requests
	import os
	import time
	import yaml

	from octoprint.util import bom_aware_open
	from octoprint.util.version import is_octoprint_compatible

	logger = log.getLogger(__name__ + ".startup")

	if connectivity_checker is not None and not connectivity_checker.online:
		logger.info("We don't appear to be online, not fetching plugin blacklist")
		return []

	def format_blacklist(entries):
		format_entry = lambda x: "{} ({})".format(x[0], x[1]) if isinstance(x, (list, tuple)) and len(x) == 2 \
			else "{} (any)".format(x)
		return ", ".join(map(format_entry, entries))

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

	def fetch_blacklist_from_cache(path, ttl):
		if not os.path.isfile(path):
			return None

		if os.stat(path).st_mtime + ttl < time.time():
			return None

		with bom_aware_open(path, encoding="utf-8", mode="r") as f:
			result = yaml.safe_load(f)

		if isinstance(result, list):
			return result

	def fetch_blacklist_from_url(url, timeout=3, cache=None):
		result = []
		try:
			r = requests.get(url, timeout=timeout)
			result = process_blacklist(r.json())

			if cache is not None:
				try:
					with bom_aware_open(cache, encoding="utf-8", mode="w") as f:
						yaml.safe_dump(result, f)
				except:
					logger.info("Fetched plugin blacklist but couldn't write it to its cache file.")
		except:
			logger.info("Unable to fetch plugin blacklist from {}, proceeding without it.".format(url))
		return result

	try:
		# first attempt to fetch from cache
		cache_path = os.path.join(settings.getBaseFolder("data"), "plugin_blacklist.yaml")
		ttl = settings.getInt(["server", "pluginBlacklist", "ttl"])
		blacklist = fetch_blacklist_from_cache(cache_path, ttl)

		if blacklist is None:
			# no result from the cache, let's fetch it fresh
			url = settings.get(["server", "pluginBlacklist", "url"])
			timeout = settings.getFloat(["server", "pluginBlacklist", "timeout"])
			blacklist = fetch_blacklist_from_url(url, timeout=timeout, cache=cache_path)

		if blacklist is None:
			# still now result, so no blacklist
			blacklist = []

		if blacklist:
			logger.info("Blacklist processing done, "
			            "adding {} blacklisted plugin versions: {}".format(len(blacklist),
			                                                               format_blacklist(blacklist)))
		else:
			logger.info("Blacklist processing done")

		return blacklist
	except:
		logger.exception("Something went wrong while processing the plugin blacklist. Proceeding without it.")