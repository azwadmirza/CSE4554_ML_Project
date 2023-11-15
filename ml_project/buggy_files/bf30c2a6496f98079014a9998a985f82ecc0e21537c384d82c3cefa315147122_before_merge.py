	def update_command(force, apikey, host, port, httpuser, httppass, https, prefix, targets):
		"""
		Apply updates.

		If any TARGETs are provided, only those components will be updated.

		\b
		Examples:
		- octoprint plugins softwareupdate:update
		    This will update all components with a pending update
		    that can be updated.
		- octoprint plugins softwareupdate:update --force
		    This will force an update of all registered components
		    that can be updated, even if they don't have an updated
		    pending.
		- octoprint plugins softwareupdate:update octoprint
		    This will only update OctoPrint and leave any further
		    components with pending updates at their current versions.
		"""

		data = dict(force=force)
		if targets:
			data["check"] = targets

		client = create_client(apikey=apikey,
		                       host=host,
		                       port=port,
		                       httpuser=httpuser,
		                       httppass=httppass,
		                       https=https,
		                       prefix=prefix)

		flags = dict(
			waiting_for_restart=False,
			seen_close=False
		)

		def on_message(ws, msg_type, msg):
			if msg_type != "plugin" or msg["plugin"] != "softwareupdate":
				return

			plugin_message = msg["data"]
			if not "type" in plugin_message:
				return

			plugin_message_type = plugin_message["type"]
			plugin_message_data = plugin_message["data"]

			if plugin_message_type == "updating":
				click.echo("Updating {} to {}...".format(plugin_message_data["name"], plugin_message_data["target"]))

			elif plugin_message_type == "update_failed":
				click.echo("\t... failed :(")

			elif plugin_message_type == "loglines" and "loglines" in plugin_message_data:
				for entry in plugin_message_data["loglines"]:
					prefix = ">>> " if entry["stream"] == "call" else ""
					error = entry["stream"] == "stderr"
					click.echo("\t{}{}".format(prefix, entry["line"].replace("\n", "\n\t")), err=error)

			elif plugin_message_type == "success" or plugin_message_type == "restart_manually":
				results = plugin_message_data["results"] if "results" in plugin_message_data else dict()
				if results:
					click.echo("The update finished successfully.")
					if plugin_message_type == "restart_manually":
						click.echo("Please restart the OctoPrint server.")
				else:
					click.echo("No update necessary")
				ws.close()

			elif plugin_message_type == "restarting":
				flags["waiting_for_restart"] = True
				click.echo("Restarting to apply changes...")

			elif plugin_message_type == "failure":
				click.echo("Error")
				ws.close()

		def on_open(ws):
			if flags["waiting_for_restart"] and flags["seen_close"]:
				click.echo(" Reconnected!")
			else:
				click.echo("Connected to server...")

		def on_close(ws):
			if flags["waiting_for_restart"] and flags["seen_close"]:
				click.echo(".", nl=False)
			else:
				flags["seen_close"] = True
				click.echo("Disconnected from server...")

		socket = client.connect_socket(on_message=on_message,
		                               on_open=on_open,
		                               on_close=on_close)

		r = client.post_json("plugin/softwareupdate/update", data=data)
		try:
			r.raise_for_status()
		except requests.exceptions.HTTPError as e:
			click.echo("Could not get update information from server, got {}".format(e))
			sys.exit(1)

		data = r.json()
		to_be_updated = data["order"]
		checks = data["checks"]
		click.echo("Update in progress, updating:")
		for name in to_be_updated:
			click.echo("\t{}".format(name if not name in checks else checks[name]))

		socket.wait()

		if flags["waiting_for_restart"]:
			if socket.reconnect(timeout=60):
				click.echo("The update finished successfully.")
			else:
				click.echo("The update finished successfully but the server apparently didn't restart as expected.")
				click.echo("Please restart the OctoPrint server.")