	def _on_part_start(self, name, content_type, filename=None):
		"""
		Called for new parts in the multipart stream. If ``filename`` is given creates new ``file`` part (which leads
		to storage of the data as temporary file on disk), if not creates a new ``data`` part (which stores
		incoming data in memory).

		Structure of ``file`` parts:

		* ``name``: name of the part
		* ``filename``: filename associated with the part
		* ``path``: path to the temporary file storing the file's data
		* ``content_type``: content type of the part
		* ``file``: file handle for the temporary file (mode "wb", not deleted on close, will be deleted however after
		  handling of the request has finished in :func:`_handle_method`)

		Structure of ``data`` parts:

		* ``name``: name of the part
		* ``content_type``: content type of the part
		* ``data``: bytes of the part (initialized to an empty string)

		:param name: name of the part
		:param content_type: content type of the part
		:param filename: filename associated with the part.
		:return: dict describing the new part
		"""
		if filename is not None:
			# this is a file
			import tempfile
			handle = tempfile.NamedTemporaryFile(mode="wb", prefix=self._file_prefix, suffix=self._file_suffix, dir=self._path, delete=False)
			return dict(name=tornado.escape.utf8(name),
						filename=tornado.escape.utf8(filename),
						path=tornado.escape.utf8(handle.name),
						content_type=tornado.escape.utf8(content_type),
						file=handle)

		else:
			return dict(name=tornado.escape.utf8(name), content_type=tornado.escape.utf8(content_type), data=b"")