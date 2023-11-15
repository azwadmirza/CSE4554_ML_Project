	def on_comm_print_job_failed(self):
		payload = self._payload_for_print_job_event()
		if payload:
			eventManager().fire(Events.PRINT_FAILED, payload)