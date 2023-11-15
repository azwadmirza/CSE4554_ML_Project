	def initialize(self, path, default_filename=None, as_attachment=False, allow_client_caching=True,
	               access_validation=None, path_validation=None, etag_generator=None, name_generator=None,
	               mime_type_guesser=None, is_pre_compressed=False, stream_body=False):
		tornado.web.StaticFileHandler.initialize(self, os.path.abspath(path), default_filename)
		self._as_attachment = as_attachment
		self._allow_client_caching = allow_client_caching
		self._access_validation = access_validation
		self._path_validation = path_validation
		self._etag_generator = etag_generator
		self._name_generator = name_generator
		self._mime_type_guesser = mime_type_guesser
		self._is_pre_compressed = is_pre_compressed
		self._stream_body = stream_body