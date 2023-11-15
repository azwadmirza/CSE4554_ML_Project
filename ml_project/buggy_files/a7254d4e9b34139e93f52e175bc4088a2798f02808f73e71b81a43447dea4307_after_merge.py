	def f(request):
		"""
		Creates a custom wsgi and Flask request context in order to be able to process user information
		stored in the current session.

		:param request: The Tornado request for which to create the environment and context
		"""
		import flask

		wsgi_environ = WsgiInputContainer.environ(request)
		with app.request_context(wsgi_environ):
			session = app.session_interface.open_session(app, flask.request)
			user_id = session.get("user_id")
			user = None

			# Yes, using protected methods is ugly. But these used to be publicly available in former versions
			# of flask-login, there are no replacements, and seeing them renamed & hidden in a minor version release
			# without any mention in the changelog means the public API ain't strictly stable either, so we might
			# as well make our life easier here and just use them...
			if user_id is not None and app.login_manager._user_callback is not None:
				user = app.login_manager._user_callback(user_id)
			app.login_manager._update_request_context_with_user(user)

			validator(flask.request, *args)