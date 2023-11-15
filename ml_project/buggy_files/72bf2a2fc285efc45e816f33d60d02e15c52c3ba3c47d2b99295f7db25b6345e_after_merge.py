def uploadGcodeFile(target):
	input_name = "file"
	input_upload_name = input_name + "." + settings().get(["server", "uploads", "nameSuffix"])
	input_upload_path = input_name + "." + settings().get(["server", "uploads", "pathSuffix"])
	if input_upload_name in request.values and input_upload_path in request.values:
		if not target in [FileDestinations.LOCAL, FileDestinations.SDCARD]:
			return make_response("Unknown target: %s" % target, 404)

		upload = octoprint.filemanager.util.DiskFileWrapper(request.values[input_upload_name], request.values[input_upload_path])

		# Store any additional user data the caller may have passed.
		userdata = None
		if "userdata" in request.values:
			import json
			try:
				userdata = json.loads(request.values["userdata"])
			except:
				return make_response("userdata contains invalid JSON", 400)

		if target == FileDestinations.SDCARD and not settings().getBoolean(["feature", "sdSupport"]):
			return make_response("SD card support is disabled", 404)

		sd = target == FileDestinations.SDCARD
		selectAfterUpload = "select" in request.values.keys() and request.values["select"] in valid_boolean_trues
		printAfterSelect = "print" in request.values.keys() and request.values["print"] in valid_boolean_trues

		if sd:
			# validate that all preconditions for SD upload are met before attempting it
			if not (printer.is_operational() and not (printer.is_printing() or printer.is_paused())):
				return make_response("Can not upload to SD card, printer is either not operational or already busy", 409)
			if not printer.is_sd_ready():
				return make_response("Can not upload to SD card, not yet initialized", 409)

		# determine future filename of file to be uploaded, abort if it can't be uploaded
		try:
			# FileDestinations.LOCAL = should normally be target, but can't because SDCard handling isn't implemented yet
			futurePath, futureFilename = fileManager.sanitize(FileDestinations.LOCAL, upload.filename)
		except:
			futurePath = None
			futureFilename = None

		if futureFilename is None:
			return make_response("Can not upload file %s, wrong format?" % upload.filename, 415)

		if "path" in request.values and request.values["path"]:
			# we currently only support uploads to sdcard via local, so first target is local instead of "target"
			futurePath = fileManager.sanitize_path(FileDestinations.LOCAL, request.values["path"])

		# prohibit overwriting currently selected file while it's being printed
		futureFullPath = fileManager.join_path(FileDestinations.LOCAL, futurePath, futureFilename)
		futureFullPathInStorage = fileManager.path_in_storage(FileDestinations.LOCAL, futureFullPath)

		if not printer.can_modify_file(futureFullPathInStorage, sd):
			return make_response("Trying to overwrite file that is currently being printed: %s" % futureFullPath, 409)

		reselect = printer.is_current_file(futureFullPathInStorage, sd)

		def fileProcessingFinished(filename, absFilename, destination):
			"""
			Callback for when the file processing (upload, optional slicing, addition to analysis queue) has
			finished.

			Depending on the file's destination triggers either streaming to SD card or directly calls selectAndOrPrint.
			"""

			if destination == FileDestinations.SDCARD and octoprint.filemanager.valid_file_type(filename, "gcode"):
				return filename, printer.add_sd_file(filename, absFilename, selectAndOrPrint)
			else:
				selectAndOrPrint(filename, absFilename, destination)
				return filename

		def selectAndOrPrint(filename, absFilename, destination):
			"""
			Callback for when the file is ready to be selected and optionally printed. For SD file uploads this is only
			the case after they have finished streaming to the printer, which is why this callback is also used
			for the corresponding call to addSdFile.

			Selects the just uploaded file if either selectAfterUpload or printAfterSelect are True, or if the
			exact file is already selected, such reloading it.
			"""
			if octoprint.filemanager.valid_file_type(added_file, "gcode") and (selectAfterUpload or printAfterSelect or reselect):
				printer.select_file(absFilename, destination == FileDestinations.SDCARD, printAfterSelect)

		try:
			added_file = fileManager.add_file(FileDestinations.LOCAL, futureFullPathInStorage, upload, allow_overwrite=True)
		except octoprint.filemanager.storage.StorageError as e:
			if e.code == octoprint.filemanager.storage.StorageError.INVALID_FILE:
				return make_response("Could not upload the file \"{}\", invalid type".format(upload.filename), 400)
			else:
				return make_response("Could not upload the file \"{}\"".format(upload.filename), 500)

		if octoprint.filemanager.valid_file_type(added_file, "stl"):
			filename = added_file
			done = True
		else:
			filename = fileProcessingFinished(added_file, fileManager.path_on_disk(FileDestinations.LOCAL, added_file), target)
			done = not sd

		if userdata is not None:
			# upload included userdata, add this now to the metadata
			fileManager.set_additional_metadata(FileDestinations.LOCAL, added_file, "userdata", userdata)

		sdFilename = None
		if isinstance(filename, tuple):
			filename, sdFilename = filename

		eventManager.fire(Events.UPLOAD, {"name": futureFilename,
		                                  "path": filename,
		                                  "target": target,

		                                  # TODO deprecated, remove in 1.4.0
		                                  "file": filename})

		files = {}
		location = url_for(".readGcodeFile", target=FileDestinations.LOCAL, filename=filename, _external=True)
		files.update({
			FileDestinations.LOCAL: {
				"name": futureFilename,
				"path": filename,
				"origin": FileDestinations.LOCAL,
				"refs": {
					"resource": location,
					"download": url_for("index", _external=True) + "downloads/files/" + FileDestinations.LOCAL + "/" + filename
				}
			}
		})

		if sd and sdFilename:
			location = url_for(".readGcodeFile", target=FileDestinations.SDCARD, filename=sdFilename, _external=True)
			files.update({
				FileDestinations.SDCARD: {
					"name": sdFilename,
					"path": sdFilename,
					"origin": FileDestinations.SDCARD,
					"refs": {
						"resource": location
					}
				}
			})

		r = make_response(jsonify(files=files, done=done), 201)
		r.headers["Location"] = location
		return r

	elif "foldername" in request.values:
		foldername = request.values["foldername"]

		if not target in [FileDestinations.LOCAL]:
			return make_response("Unknown target: %s" % target, 400)

		futurePath, futureName = fileManager.sanitize(target, foldername)
		if not futureName or not futurePath:
			return make_response("Can't create a folder with an empty name", 400)

		if "path" in request.values and request.values["path"]:
			futurePath = fileManager.sanitize_path(FileDestinations.LOCAL,
			                                       request.values["path"])

		futureFullPath = fileManager.join_path(target, futurePath, futureName)
		if octoprint.filemanager.valid_file_type(futureName):
			return make_response("Can't create a folder named %s, please try another name" % futureName, 409)

		try:
			added_folder = fileManager.add_folder(target, futureFullPath)
		except octoprint.filemanager.storage.StorageError as e:
			if e.code == octoprint.filemanager.storage.StorageError.INVALID_DIRECTORY:
				return make_response("Could not create folder {}, invalid directory".format(futureName))
			else:
				return make_response("Could not create folder {}".format(futureName))

		location = url_for(".readGcodeFile",
		                   target=FileDestinations.LOCAL,
		                   filename=added_folder,
		                   _external=True)
		folder = dict(name=futureName,
		              path=added_folder,
		              origin=target,
		              refs=dict(resource=location))

		r = make_response(jsonify(folder=folder, done=True), 201)
		r.headers["Location"] = location
		return r

	else:
		return make_response("No file to upload and no folder to create", 400)