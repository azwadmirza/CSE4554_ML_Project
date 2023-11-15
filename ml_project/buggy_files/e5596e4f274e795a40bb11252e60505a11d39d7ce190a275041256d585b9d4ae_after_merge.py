def login():
	data = request.values
	if hasattr(request, "json") and request.json:
		data = request.json

	if octoprint.server.userManager.enabled and "user" in data and "pass" in data:
		username = data["user"]
		password = data["pass"]

		if "remember" in data and data["remember"] in valid_boolean_trues:
			remember = True
		else:
			remember = False

		if "usersession.id" in session:
			_logout(current_user)

		user = octoprint.server.userManager.findUser(username)
		if user is not None:
			if octoprint.server.userManager.checkPassword(username, password):
				if not user.is_active():
					return make_response(("Your account is deactivated", 403, []))

				if octoprint.server.userManager.enabled:
					user = octoprint.server.userManager.login_user(user)
					session["usersession.id"] = user.session
					g.user = user
				login_user(user, remember=remember)
				identity_changed.send(current_app._get_current_object(), identity=Identity(user.get_id()))

				remote_addr = get_remote_address(request)
				logging.getLogger(__name__).info("Actively logging in user {} from {}".format(user.get_id(), remote_addr))

				response = user.asDict()
				response["_is_external_client"] = s().getBoolean(["server", "ipCheck", "enabled"]) \
				                                  and not util_net.is_lan_address(remote_addr,
				                                                                  additional_private=s().get(["server", "ipCheck", "trustedSubnets"]))

				r = make_response(jsonify(response))
				r.delete_cookie("active_logout")
				return r

		return make_response(("User unknown or password incorrect", 401, []))

	elif "passive" in data:
		return passive_login()
	return NO_CONTENT