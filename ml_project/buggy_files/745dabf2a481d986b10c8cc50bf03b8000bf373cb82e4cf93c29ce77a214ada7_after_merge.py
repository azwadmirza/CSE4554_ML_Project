def _getFileList(origin, path=None, filter=None, recursive=False, allow_from_cache=True):
	if origin == FileDestinations.SDCARD:
		sdFileList = printer.get_sd_files()

		files = []
		if sdFileList is not None:
			for sdFile, sdSize in sdFileList:
				type_path = octoprint.filemanager.get_file_type(sdFile)
				if not type_path:
					# only supported extensions
					continue
				else:
					file_type = type_path[0]

				file = {
					"type": file_type,
					"typePath": type_path,
					"name": sdFile,
					"display": sdFile,
					"path": sdFile,
					"origin": FileDestinations.SDCARD,
					"refs": {
						"resource": url_for(".readGcodeFile", target=FileDestinations.SDCARD, filename=sdFile, _external=True)
					}
				}
				if sdSize is not None:
					file.update({"size": sdSize})
				files.append(file)
	else:
		filter_func = None
		if filter:
			filter_func = lambda entry, entry_data: octoprint.filemanager.valid_file_type(entry, type=filter)

		with _file_cache_mutex:
			cache_key = "{}:{}:{}:{}".format(origin, path, recursive, filter)
			files, lastmodified = _file_cache.get(cache_key, ([], None))
			# recursive needs to be True for lastmodified queries so we get lastmodified of whole subtree - #3422
			if not allow_from_cache or lastmodified is None or lastmodified < fileManager.last_modified(origin, path=path, recursive=True):
				files = list(fileManager.list_files(origin, path=path, filter=filter_func, recursive=recursive)[origin].values())
				lastmodified = fileManager.last_modified(origin, path=path, recursive=True)
				_file_cache[cache_key] = (files, lastmodified)

		def analyse_recursively(files, path=None):
			if path is None:
				path = ""

			result = []
			for file_or_folder in files:
				# make a shallow copy in order to not accidentally modify the cached data
				file_or_folder = dict(file_or_folder)

				file_or_folder["origin"] = FileDestinations.LOCAL

				if file_or_folder["type"] == "folder":
					if "children" in file_or_folder:
						file_or_folder["children"] = analyse_recursively(file_or_folder["children"].values(), path + file_or_folder["name"] + "/")

					file_or_folder["refs"] = dict(resource=url_for(".readGcodeFile", target=FileDestinations.LOCAL, filename=path + file_or_folder["name"], _external=True))
				else:
					if "analysis" in file_or_folder and octoprint.filemanager.valid_file_type(file_or_folder["name"], type="gcode"):
						file_or_folder["gcodeAnalysis"] = file_or_folder["analysis"]
						del file_or_folder["analysis"]

					if "history" in file_or_folder and octoprint.filemanager.valid_file_type(file_or_folder["name"], type="gcode"):
						# convert print log
						history = file_or_folder["history"]
						del file_or_folder["history"]
						success = 0
						failure = 0
						last = None
						for entry in history:
							success += 1 if "success" in entry and entry["success"] else 0
							failure += 1 if "success" in entry and not entry["success"] else 0
							if not last or ("timestamp" in entry and "timestamp" in last and entry["timestamp"] > last["timestamp"]):
								last = entry
						if last:
							prints = dict(
								success=success,
								failure=failure,
								last=dict(
									success=last["success"],
									date=last["timestamp"]
								)
							)
							if "printTime" in last:
								prints["last"]["printTime"] = last["printTime"]
							file_or_folder["prints"] = prints

					file_or_folder["refs"] = dict(resource=url_for(".readGcodeFile", target=FileDestinations.LOCAL, filename=file_or_folder["path"], _external=True),
					                              download=url_for("index", _external=True) + "downloads/files/" + FileDestinations.LOCAL + "/" + file_or_folder["path"])

				result.append(file_or_folder)

			return result

		files = analyse_recursively(files)

	return files