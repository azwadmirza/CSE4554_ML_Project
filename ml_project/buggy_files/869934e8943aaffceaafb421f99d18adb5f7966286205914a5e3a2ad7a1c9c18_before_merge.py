def loginUserFromApiKey():
	apikey = get_api_key(_flask.request)

	if not apikey:
		return False

	if octoprint.server.appSessionManager.validate(apikey):
		return False

	user = get_user_for_apikey(apikey)
	if not loginUser(user):
		raise InvalidApiKeyException()
	else:
		return True