	def _work(self):
		while True:
			self._change_event.wait()

			now = time.time()
			delta = now - self._last_update
			additional_wait_time = self._interval - delta
			if additional_wait_time > 0:
				time.sleep(additional_wait_time)

			with self._state_lock:
				data = self.get_current_data()
				self._update_callback(data)
				self._last_update = time.time()
				self._change_event.clear()