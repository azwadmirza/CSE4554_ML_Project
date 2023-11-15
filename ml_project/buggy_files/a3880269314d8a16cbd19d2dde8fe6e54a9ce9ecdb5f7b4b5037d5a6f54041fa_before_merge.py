def _create_lastmodified(path, recursive):
	if path.endswith("/files"):
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

	elif path.endswith("/files/local"):
		# only local storage involved
		try:
			return fileManager.last_modified(FileDestinations.LOCAL, recursive=recursive)
		except Exception:
			logging.getLogger(__name__).exception("There was an error retrieving the last modified data from storage {}".format(FileDestinations.LOCAL))
			return None

	else:
		return None