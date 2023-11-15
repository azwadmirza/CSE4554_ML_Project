def get_flask_user_from_request(request):
	"""
	Retrieves the current flask user from the request context. Uses API key if available, otherwise the current
	user session if available.

	:param request: flask request from which to retrieve the current user
	:return: the user or None if no user could be determined
	"""
	import octoprint.server.util
	import flask_login

	user = None

	apikey = octoprint.server.util.get_api_key(request)
	if apikey is not None:
		user = octoprint.server.util.get_user_for_apikey(apikey)

	if user is None:
		user = flask_login.current_user

	return user