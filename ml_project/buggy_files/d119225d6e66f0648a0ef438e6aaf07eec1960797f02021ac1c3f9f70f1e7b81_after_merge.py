	def on_comm_print_job_done(self):
		self._fileManager.delete_recovery_data()

		payload = self._payload_for_print_job_event()
		if payload:
			payload["time"] = self._comm.getPrintTime()
			self._updateProgressData(completion=1.0,
			                         filepos=payload["size"],
			                         printTime=payload["time"],
			                         printTimeLeft=0)
			self._stateMonitor.set_state(self._dict(text=self.get_state_string(), flags=self._getStateFlags()))

			eventManager().fire(Events.PRINT_DONE, payload)
			self.script("afterPrintDone",
			            context=dict(event=payload),
			            must_be_set=False)

			def log_print():
				self._fileManager.log_print(payload["origin"],
				                            payload["path"],
				                            time.time(),
				                            payload["time"],
				                            True,
				                            self._printerProfileManager.get_current_or_default()["id"])

			thread = threading.Thread(target=log_print)
			thread.daemon = True
			thread.start()

		else:
			self._updateProgressData()
			self._stateMonitor.set_state(self._dict(text=self.get_state_string(), flags=self._getStateFlags()))