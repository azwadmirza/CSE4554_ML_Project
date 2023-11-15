	def on_comm_print_job_started(self, suppress_script=False):
		self._stateMonitor.trigger_progress_update()
		payload = self._payload_for_print_job_event()
		if payload:
			eventManager().fire(Events.PRINT_STARTED, payload)
			if not suppress_script:
				self.script("beforePrintStarted",
				            context=dict(event=payload),
				            part_of_job=True,
				            must_be_set=False)