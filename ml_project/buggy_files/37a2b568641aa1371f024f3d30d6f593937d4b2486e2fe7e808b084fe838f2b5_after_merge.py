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

			default_port = "443" if scheme == "https" else "80"
			host = host.strip()

			if ":" in host:
				# we might have an ipv6 address here, or a port, or both

				if host[0] == "[":
					# that looks like an ipv6 address with port, e.g. [fec1::1]:80
					address_end = host.find("]")
					if address_end == -1:
						# no ], that looks like a seriously broken address
						return None, None

					# extract server ip, skip enclosing [ and ]
					server = host[1:address_end]
					tail = host[address_end + 1:]

					# now check if there's also a port
					if len(tail) and tail[0] == ":":
						# port included as well
						port = tail[1:]
					else:
						# no port, use default one
						port = default_port

				elif self.__class__.valid_ip(host):
					# ipv6 address without port
					server = host
					port = default_port

				else:
					# ipv4 address with port
					server, port = host.rsplit(":", 1)

			else:
				server = host
				port = default_port

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
				server_name_component = environ["SERVER_NAME"]
				if ":" in server_name_component and self.__class__.valid_ip(server_name_component):
					# this is an ipv6 address, we need to wrap that in [ and ] before appending the port
					server_name_component = "[" + server_name_component + "]"

				environ["HTTP_HOST"] = server_name_component + ":" + environ["SERVER_PORT"]

		# call wrapped app with rewritten environment
		return environ