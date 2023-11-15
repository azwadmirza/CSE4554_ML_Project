def passive_login():
	logger = logging.getLogger(__name__)

	if octoprint.server.userManager.enabled:
		user = octoprint.server.userManager.login_user(flask_login.current_user)
	else:
		user = flask_login.current_user

	remote_address = get_remote_address(flask.request)
	ip_check_enabled = settings().getBoolean(["server", "ipCheck", "enabled"])
	ip_check_trusted = settings().get(["server", "ipCheck", "trustedSubnets"])

	if user is not None and not user.is_anonymous() and user.is_active():
		flask_principal.identity_changed.send(flask.current_app._get_current_object(),
		                                      identity=flask_principal.Identity(user.get_id()))
		if hasattr(user, "session"):
			flask.session["usersession.id"] = user.session
		flask.g.user = user

		logger.info("Passively logging in user {} from {}".format(user.get_id(), remote_address))

		response = user.asDict()
		response["_is_external_client"] = ip_check_enabled and not is_lan_address(remote_address,
		                                                                          additional_private=ip_check_trusted)
		return flask.jsonify(response)

	elif settings().getBoolean(["accessControl", "autologinLocal"]) \
			and settings().get(["accessControl", "autologinAs"]) is not None \
			and settings().get(["accessControl", "localNetworks"]) is not None:

		autologin_as = settings().get(["accessControl", "autologinAs"])
		local_networks = _local_networks()
		logger.debug("Checking if remote address {} is in localNetworks ({!r})".format(remote_address, local_networks))

		try:
			if netaddr.IPAddress(remote_address) in local_networks:
				user = octoprint.server.userManager.findUser(autologin_as)
				if user is not None and user.is_active():
					user = octoprint.server.userManager.login_user(user)
					flask.session["usersession.id"] = user.session
					flask.g.user = user
					flask_login.login_user(user)
					flask_principal.identity_changed.send(flask.current_app._get_current_object(),
					                                      identity=flask_principal.Identity(user.get_id()))

					logger.info("Passively logging in user {} from {} via autologin".format(user.get_id(),
					                                                                        remote_address))

					response = user.asDict()
					response["_is_external_client"] = ip_check_enabled and not is_lan_address(remote_address,
					                                                                          additional_private=ip_check_trusted)
					return flask.jsonify(response)
		except:
			logger.exception("Could not autologin user {} for networks {}".format(autologin_as, local_networks))

	return "", 204