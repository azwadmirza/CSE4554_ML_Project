	def on_comm_print_job_cancelled(self):
		self._setCurrentZ(None)
		self._updateProgressData()
		self._setPrintingUser(None)

		payload = self._payload_for_print_job_event(position=self._comm.cancel_position.as_dict() if self._comm and self._comm.cancel_position else None)
		if payload:
			payload["time"] = self._comm.getPrintTime()

			eventManager().fire(Events.PRINT_CANCELLED, payload)
			self.script("afterPrintCancelled",
			            context=dict(event=payload),
			            must_be_set=False)

			def finalize():
				self._fileManager.log_print(payload["origin"],
				                            payload["path"],
				                            time.time(),
				                            payload["time"],
				                            False,
				                            self._printerProfileManager.get_current_or_default()["id"])
				eventManager().fire(Events.PRINT_FAILED, payload)

			thread = threading.Thread(target=finalize)
			thread.daemon = True
			thread.start()