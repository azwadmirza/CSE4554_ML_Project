	def _list_folder(self, path, base="", entry_filter=None, recursive=True, **kwargs):
		if entry_filter is None:
			entry_filter = kwargs.get("filter", None)

		metadata = self._get_metadata(path)
		if not metadata:
			metadata = dict()
		metadata_dirty = False

		result = dict()
		for entry in scandir(path):
			if is_hidden_path(entry.name):
				# no hidden files and folders
				continue

			try:
				entry_name = entry_display = entry.name
				entry_path = entry.path
				entry_is_file = entry.is_file()
				entry_is_dir = entry.is_dir()
				entry_stat = entry.stat()
			except:
				# error while trying to fetch file metadata, that might be thanks to file already having
				# been moved or deleted - ignore it and continue
				continue

			try:
				new_entry_name, new_entry_path = self._sanitize_entry(entry_name, path, entry_path)
				if entry_name != new_entry_name or entry_path != new_entry_path:
					entry_display = to_unicode(entry_name)
					entry_name = new_entry_name
					entry_path = new_entry_path
					entry_stat = os.stat(entry_path)
			except:
				# error while trying to rename the file, we'll continue here and ignore it
				continue

			path_in_location = entry_name if not base else base + entry_name

			try:
				# file handling
				if entry_is_file:
					type_path = octoprint.filemanager.get_file_type(entry_name)
					if not type_path:
						# only supported extensions
						continue
					else:
						file_type = type_path[0]

					if entry_name in metadata and isinstance(metadata[entry_name], dict):
						entry_metadata = metadata[entry_name]
						if not "display" in entry_metadata and entry_display != entry_name:
							metadata[entry_name]["display"] = entry_display
							entry_metadata["display"] = entry_display
							metadata_dirty = True
					else:
						entry_metadata = self._add_basic_metadata(path, entry_name,
						                                          display_name=entry_display,
						                                          save=False,
						                                          metadata=metadata)
						metadata_dirty = True

					# TODO extract model hash from source if possible to recreate link

					if not entry_filter or entry_filter(entry_name, entry_metadata):
						# only add files passing the optional filter
						extended_entry_data = dict()
						extended_entry_data.update(entry_metadata)
						extended_entry_data["name"] = entry_name
						extended_entry_data["display"] = entry_metadata.get("display", entry_name)
						extended_entry_data["path"] = path_in_location
						extended_entry_data["type"] = file_type
						extended_entry_data["typePath"] = type_path
						stat = entry_stat
						if stat:
							extended_entry_data["size"] = stat.st_size
							extended_entry_data["date"] = int(stat.st_mtime)

						result[entry_name] = extended_entry_data

				# folder recursion
				elif entry_is_dir:
					if entry_name in metadata and isinstance(metadata[entry_name], dict):
						entry_metadata = metadata[entry_name]
						if not "display" in entry_metadata and entry_display != entry_name:
							metadata[entry_name]["display"] = entry_display
							entry_metadata["display"] = entry_display
							metadata_dirty = True
					elif entry_name != entry_display:
						entry_metadata = self._add_basic_metadata(path, entry_name,
						                                          display_name=entry_display,
						                                          save=False,
						                                          metadata=metadata)
						metadata_dirty = True
					else:
						entry_metadata = dict()

					entry_data = dict(
						name=entry_name,
						display=entry_metadata.get("display", entry_name),
						path=path_in_location,
						type="folder",
						typePath=["folder"]
					)
					if recursive:
						sub_result = self._list_folder(entry_path, base=path_in_location + "/", entry_filter=entry_filter,
						                               recursive=recursive)
						entry_data["children"] = sub_result

					if not entry_filter or entry_filter(entry_name, entry_data):
						def get_size():
							total_size = 0
							for element in entry_data["children"].values():
								if "size" in element:
									total_size += element["size"]

							return total_size

						# only add folders passing the optional filter
						extended_entry_data = dict()
						extended_entry_data.update(entry_data)
						if recursive:
							extended_entry_data["size"] = get_size()

						result[entry_name] = extended_entry_data
			except:
				# So something went wrong somewhere while processing this file entry - log that and continue
				self._logger.exception("Error while processing entry {}".format(entry_path))
				continue

		# TODO recreate links if we have metadata less entries

		# save metadata
		if metadata_dirty:
			self._save_metadata(path, metadata)

		return result