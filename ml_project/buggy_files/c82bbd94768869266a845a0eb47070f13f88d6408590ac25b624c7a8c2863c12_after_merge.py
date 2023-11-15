	def handle_request(self):
		data = flask.request.json
		if data is None:
			return flask.make_response("Missing key request", 400)

		if not "app" in data:
			return flask.make_response("No app name provided", 400)

		app_name = data["app"]
		user_id = None
		if "user" in data and data["user"]:
			user_id = data["user"]

		app_token, user_token = self._add_pending_decision(app_name, user_id=user_id)

		self._plugin_manager.send_plugin_message(self._identifier, dict(type="request_access",
		                                                                app_name=app_name,
		                                                                user_token=user_token,
		                                                                user_id=user_id))
		response = flask.jsonify(app_token=app_token)
		response.status_code = 201
		response.headers["Location"] = flask.url_for(".handle_decision_poll", app_token=app_token, _external=True)
		return response