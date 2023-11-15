	def on_comm_file_selected(self, full_path, size, sd, user=None):
		if full_path is not None:
			payload = self._payload_for_print_job_event(location=FileDestinations.SDCARD if sd else FileDestinations.LOCAL,
			                                            print_job_file=full_path)
			eventManager().fire(Events.FILE_SELECTED, payload)
		else:
			eventManager().fire(Events.FILE_DESELECTED)

		self._setJobData(full_path, size, sd, user=user)
		self._stateMonitor.set_state(self._dict(text=self.get_state_string(), flags=self._getStateFlags()))

		if self._printAfterSelect:
			self._printAfterSelect = False
			self.start_print(pos=self._posAfterSelect, user=user)