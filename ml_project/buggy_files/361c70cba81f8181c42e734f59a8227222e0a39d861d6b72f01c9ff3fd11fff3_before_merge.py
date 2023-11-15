	def _track_printjob_event(self, event, payload):
		if not self._settings.get_boolean(["events", "printjob"]):
			return

		unique_id = self._settings.get([b"unique_id"])
		if not unique_id:
			return

		sha = hashlib.sha1()
		sha.update(payload.get("path"))
		sha.update(unique_id)

		track_event = None
		args = dict(origin=payload.get(b"origin"), file=sha.hexdigest())

		if event == Events.PRINT_STARTED:
			track_event = "print_started"
		elif event == Events.PRINT_DONE:
			try:
				elapsed = int(payload.get(b"time"))
				args[b"elapsed"] = elapsed
			except ValueError:
				pass
			track_event = "print_done"
		elif event == Events.PRINT_FAILED:
			try:
				elapsed = int(payload.get(b"time"))
				args[b"elapsed"] = elapsed
			except ValueError:
				pass
			args[b"reason"] = payload.get(b"reason", "unknown")

			if b"error" in payload and self._settings.get_boolean(["events", "commerror"]):
				args[b"commerror_text"] = payload[b"error"]

			track_event = "print_failed"
		elif event == Events.PRINT_CANCELLED:
			try:
				elapsed = int(payload.get(b"time"))
				args[b"elapsed"] = elapsed
			except ValueError:
				pass
			track_event = "print_cancelled"

		if callable(self._helpers_get_throttle_state):
			try:
				throttle_state = self._helpers_get_throttle_state(run_now=True)
				if throttle_state and (throttle_state.get(b"current_issue", False) or throttle_state.get(b"past_issue", False)):
					args[b"throttled_now"] = throttle_state[b"current_issue"]
					args[b"throttled_past"] = throttle_state[b"past_issue"]
					args[b"throttled_mask"] = throttle_state[b"raw_value"]
			except:
				# ignored
				pass

		if track_event is not None:
			self._track(track_event, **args)