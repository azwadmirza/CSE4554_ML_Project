	def __call__(self, environ):
		def retrieve_header(header_type):
			candidates = getattr(self, "_headers_" + header_type, [])
			fallback = getattr(self, "_fallback_" + header_type, None)

			for candidate in candidates:
				value = environ.get(candidate, None)
				if value is not None:
					return value
			else:
				return fallback

		def host_to_server_and_port(host, scheme):
			if host is None:
				return None, None

			if ":" in host:
				server, port = host.split(":", 1)
			else:
				server = host
				port = "443" if scheme == "https" else "80"

			return server, port

		# determine prefix
		prefix = retrieve_header("prefix")
		if prefix is not None:
			environ["SCRIPT_NAME"] = prefix
			path_info = environ["PATH_INFO"]
			if path_info.startswith(prefix):
				environ["PATH_INFO"] = path_info[len(prefix):]

		# determine scheme
		scheme = retrieve_header("scheme")
		if scheme is not None and "," in scheme:
			# Scheme might be something like "https,https" if doubly-reverse-proxied
			# without stripping original scheme header first, make sure to only use
			# the first entry in such a case. See #1391.
			scheme, _ = map(lambda x: x.strip(), scheme.split(",", 1))
		if scheme is not None:
			environ["wsgi.url_scheme"] = scheme

		# determine host
		url_scheme = environ["wsgi.url_scheme"]
		host = retrieve_header("host")
		if host is not None:
			# if we have a host, we take server_name and server_port from it
			server, port = host_to_server_and_port(host, url_scheme)
			environ["HTTP_HOST"] = host
			environ["SERVER_NAME"] = server
			environ["SERVER_PORT"] = port

		elif environ.get("HTTP_HOST", None) is not None:
			# if we have a Host header, we use that and make sure our server name and port properties match it
			host = environ["HTTP_HOST"]
			server, port = host_to_server_and_port(host, url_scheme)
			environ["SERVER_NAME"] = server
			environ["SERVER_PORT"] = port

		else:
			# else we take a look at the server and port headers and if we have
			# something there we derive the host from it

			# determine server - should usually not be used
			server = retrieve_header("server")
			if server is not None:
				environ["SERVER_NAME"] = server

			# determine port - should usually not be used
			port = retrieve_header("port")
			if port is not None:
				environ["SERVER_PORT"] = port

			# reconstruct host header
			if url_scheme == "http" and environ["SERVER_PORT"] == "80" or url_scheme == "https" and environ["SERVER_PORT"] == "443":
				# default port for scheme, can be skipped
				environ["HTTP_HOST"] = environ["SERVER_NAME"]
			else:
				environ["HTTP_HOST"] = environ["SERVER_NAME"] + ":" + environ["SERVER_PORT"]

		# call wrapped app with rewritten environment
		return environ