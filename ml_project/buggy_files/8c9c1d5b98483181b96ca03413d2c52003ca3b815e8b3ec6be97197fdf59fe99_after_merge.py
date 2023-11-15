	def get(self, path, include_body=True):
		if self._access_validation is not None:
			self._access_validation(self.request)
		if self._path_validation is not None:
			self._path_validation(path)

		if "cookie" in self.request.arguments:
			self.set_cookie(self.request.arguments["cookie"][0], "true", path="/")

		if self.should_use_precompressed():
			if os.path.exists(os.path.join(self.root, path + ".gz")):
				self.set_header("Content-Encoding", "gzip")
				path = path + ".gz"
			else:
				logging.getLogger(__name__).warning("Precompressed assets expected but {}.gz does not exist "
				                                    "in {}, using plain file instead.".format(path, self.root))

		if self._stream_body:
			return self.streamed_get(path, include_body=include_body)
		else:
			return tornado.web.StaticFileHandler.get(self, path, include_body=include_body)