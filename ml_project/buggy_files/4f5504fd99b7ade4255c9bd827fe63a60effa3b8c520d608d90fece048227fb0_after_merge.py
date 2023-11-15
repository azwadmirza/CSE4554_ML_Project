def get_flask_user_from_request(request):
	"""
	Retrieves the current flask user from the request context. Uses API key if available, otherwise the current
	user session if available.

	:param request: flask request from which to retrieve the current user
	:return: the user (might be an anonymous user)
	"""
	import octoprint.server.util
	import flask_login

	user = None

	apikey = octoprint.server.util.get_api_key(request)
	if apikey is not None:
		# user from api key?
		user = octoprint.server.util.get_user_for_apikey(apikey)

	if user is None:
		# user still None -> current session user
		user = flask_login.current_user

	if user is None:
		# user still None -> anonymous
		from octoprint.server import userManager
		user = userManager.anonymous_user_factory()

	return user