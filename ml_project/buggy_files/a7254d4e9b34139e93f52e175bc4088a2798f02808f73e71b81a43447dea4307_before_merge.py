	def f(request):
		"""
		Creates a custom wsgi and Flask request context in order to be able to process user information
		stored in the current session.

		:param request: The Tornado request for which to create the environment and context
		"""
		import flask

		wsgi_environ = WsgiInputContainer.environ(request)
		with app.request_context(wsgi_environ):
			app.session_interface.open_session(app, flask.request)
			app.login_manager.reload_user()
			validator(flask.request, *args)