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