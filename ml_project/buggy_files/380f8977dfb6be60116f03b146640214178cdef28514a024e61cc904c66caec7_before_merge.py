		def host_to_server_and_port(host, scheme):
			if host is None:
				return None, None

			if ":" in host:
				server, port = host.split(":", 1)
			else:
				server = host
				port = "443" if scheme == "https" else "80"

			return server, port