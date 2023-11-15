	def _on_request_body_finish(self):
		"""
		Called when the request body has been read completely. Takes care of creating the replacement body out of the
		logged parts, turning ``file`` parts into new ``data`` parts.
		"""

		self._new_body = b""
		for name, part in self._parts.items():
			if "filename" in part:
				# add form fields for filename, path, size and content_type for all files contained in the request
				if not "path" in part:
					continue

				parameters = dict(
					name=part["filename"],
					path=part["path"],
					size=str(os.stat(part["path"]).st_size)
				)
				if "content_type" in part:
					parameters["content_type"] = part["content_type"]

				fields = dict((self._suffixes[key], value) for (key, value) in parameters.items())
				for n, p in fields.items():
					if n is None or p is None:
						continue
					key = name + b"." + octoprint.util.to_bytes(n)
					self._new_body += b"--%s\r\n" % self._multipart_boundary
					self._new_body += b"Content-Disposition: form-data; name=\"%s\"\r\n" % key
					self._new_body += b"Content-Type: text/plain; charset=utf-8\r\n"
					self._new_body += b"\r\n"
					self._new_body += octoprint.util.to_bytes(p) + b'\r\n'
			elif "data" in part:
				self._new_body += b"--%s\r\n" % self._multipart_boundary
				value = part["data"]
				self._new_body += b"Content-Disposition: form-data; name=\"%s\"\r\n" % name
				if "content_type" in part and part["content_type"] is not None:
					self._new_body += b"Content-Type: %s\r\n" % part["content_type"]
				self._new_body += b"\r\n"
				self._new_body += value + b"\r\n"
		self._new_body += b"--%s--\r\n" % self._multipart_boundary