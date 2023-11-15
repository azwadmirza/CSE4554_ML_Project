def _create_etag(path, filter, recursive, lm=None):
	if lm is None:
		lm = _create_lastmodified(path, recursive)

	if lm is None:
		return None

	hash = hashlib.sha1()
	def hash_update(value):
		value = value.encode('utf-8')
		hash.update(value)
	hash_update(str(lm))
	hash_update(str(filter))
	hash_update(str(recursive))

	path = path[len("/api/files"):]
	if path.startswith("/"):
		path = path[1:]

	if "/" in path:
		storage, _ = path.split("/", 1)
	else:
		storage = path

	if path == "" or storage == FileDestinations.SDCARD:
		# include sd data in etag
		hash_update(repr(sorted(printer.get_sd_files(), key=lambda x: sv(x[0]))))

	hash_update(_DATA_FORMAT_VERSION) # increment version if we change the API format

	return hash.hexdigest()