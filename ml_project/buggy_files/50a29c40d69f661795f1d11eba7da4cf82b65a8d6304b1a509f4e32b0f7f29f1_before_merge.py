	def _repeatedly_check(self, path, interval=1, stable=5):
		last_size = os.stat(path).st_size
		countdown = stable

		while True:
			new_size = os.stat(path).st_size
			if new_size == last_size:
				self._logger.debug("File at {} is no longer growing, counting down: {}".format(path, countdown))
				countdown -= 1
				if countdown <= 0:
					break
			else:
				self._logger.debug("File at {} is still growing, waiting...".format(path))
				countdown = stable

			time.sleep(interval)

		self._logger.debug("File at {} is stable, moving it".format(path))
		self._upload(path)