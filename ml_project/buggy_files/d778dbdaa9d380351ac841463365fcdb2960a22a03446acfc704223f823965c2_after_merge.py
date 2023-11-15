def permission_validator(request, permission):
	"""
	Validates that the given request is made by an authorized user, identified either by API key or existing Flask
	session.

	Must be executed in an existing Flask request context!

	:param request: The Flask request object
	:param request: The required permission
	"""

	user = get_flask_user_from_request(request)
	if not user.has_permission(permission):
		raise tornado.web.HTTPError(403)