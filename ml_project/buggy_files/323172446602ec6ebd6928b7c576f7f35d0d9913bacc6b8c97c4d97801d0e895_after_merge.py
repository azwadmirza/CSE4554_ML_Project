	def environ(request, body=None):
		"""
		Converts a ``tornado.httputil.HTTPServerRequest`` to a WSGI environment.

		An optional ``body`` to be used for populating ``wsgi.input`` can be supplied (either a string or a stream). If not
		supplied, ``request.body`` will be wrapped into a ``io.BytesIO`` stream and used instead.

		:param request: the ``tornado.httpserver.HTTPServerRequest`` to derive the WSGI environment from
		:param body: an optional body  to use as ``wsgi.input`` instead of ``request.body``, can be a string or a stream
		"""
		from tornado.wsgi import to_wsgi_str
		import sys
		import io

		# determine the request_body to supply as wsgi.input
		if body is not None:
			if isinstance(body, (bytes, str, unicode)):
				request_body = io.BytesIO(tornado.escape.utf8(body))
			else:
				request_body = body
		else:
			request_body = io.BytesIO(tornado.escape.utf8(request.body))

		hostport = request.host.split(":")
		if len(hostport) == 2:
			host = hostport[0]
			port = int(hostport[1])
		else:
			host = request.host
			port = 443 if request.protocol == "https" else 80
		environ = {
		"REQUEST_METHOD": request.method,
		"SCRIPT_NAME": "",
		"PATH_INFO": to_wsgi_str(tornado.escape.url_unescape(
			request.path, encoding=None, plus=False)),
		"QUERY_STRING": request.query,
		"REMOTE_ADDR": request.remote_ip,
		"SERVER_NAME": host,
		"SERVER_PORT": str(port),
		"SERVER_PROTOCOL": request.version,
		"wsgi.version": (1, 0),
		"wsgi.url_scheme": request.protocol,
		"wsgi.input": request_body,
		"wsgi.errors": sys.stderr,
		"wsgi.multithread": False,
		"wsgi.multiprocess": True,
		"wsgi.run_once": False,
		}
		if "Content-Type" in request.headers:
			environ["CONTENT_TYPE"] = request.headers.pop("Content-Type")
		if "Content-Length" in request.headers:
			environ["CONTENT_LENGTH"] = request.headers.pop("Content-Length")
		for key, value in request.headers.items():
			environ["HTTP_" + key.replace("-", "_").upper()] = value
		return environ