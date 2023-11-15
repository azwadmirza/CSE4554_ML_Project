		def __init__(self, path, target):
			self.finished = threading.Event()
			self.finished.clear()

			self.comm = None
			self.error = False
			self.started = False

			self._path = path
			self._target = target
			self._state = None