	def _upload(self, path):
		try:
			file_wrapper = octoprint.filemanager.util.DiskFileWrapper(os.path.basename(path), path)

			# determine future filename of file to be uploaded, abort if it can't be uploaded
			try:
				futurePath, futureFilename = self._file_manager.sanitize(octoprint.filemanager.FileDestinations.LOCAL, file_wrapper.filename)
			except:
				futurePath = None
				futureFilename = None

			if futureFilename is None or (len(self._file_manager.registered_slicers) == 0 and not octoprint.filemanager.valid_file_type(futureFilename)):
				return

			# prohibit overwriting currently selected file while it's being printed
			futureFullPath = self._file_manager.join_path(octoprint.filemanager.FileDestinations.LOCAL, futurePath, futureFilename)
			futureFullPathInStorage = self._file_manager.path_in_storage(octoprint.filemanager.FileDestinations.LOCAL, futureFullPath)

			if not self._printer.can_modify_file(futureFullPathInStorage, False):
				return

			reselect = self._printer.is_current_file(futureFullPathInStorage, False)

			added_file = self._file_manager.add_file(octoprint.filemanager.FileDestinations.LOCAL,
			                                         file_wrapper.filename,
			                                         file_wrapper,
			                                         allow_overwrite=True)
			if os.path.exists(path):
				try:
					os.remove(path)
				except:
					pass

			if reselect:
				self._printer.select_file(self._file_manager.path_on_disk(octoprint.filemanager.FileDestinations.LOCAL,
				                                                          added_file),
				                          False)
		except:
			self._logger.exception("There was an error while processing the file {} in the watched folder".format(path))