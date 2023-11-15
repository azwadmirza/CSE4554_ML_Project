def _create_lastmodified(path, recursive):
	path = path[len("/api/files"):]
	if path.startswith("/"):
		path = path[1:]

	if path == "":
		# all storages involved
		lms = [0]
		for storage in fileManager.registered_storages:
			try:
				lms.append(fileManager.last_modified(storage, recursive=recursive))
			except Exception:
				logging.getLogger(__name__).exception("There was an error retrieving the last modified data from storage {}".format(storage))
				lms.append(None)

		if any(filter(lambda x: x is None, lms)):
			# we return None if ANY of the involved storages returned None
			return None

		# if we reach this point, we return the maximum of all dates
		return max(lms)

	else:
		storage, path_in_storage = path.split("/", 1)
		try:
			return fileManager.last_modified(storage, path=path_in_storage, recursive=recursive)
		except Exception:
			logging.getLogger(__name__).exception("There was an error retrieving the last modified data from storage {} and path {}".format(storage, path_in_storage))
			return None