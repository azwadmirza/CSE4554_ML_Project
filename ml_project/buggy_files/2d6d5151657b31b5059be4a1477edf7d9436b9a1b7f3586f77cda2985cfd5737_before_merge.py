	def __init__(self):
		self._logger = logging.getLogger(__name__)

		self.on_log_call = lambda *args, **kwargs: None
		"""Callback for the called command line"""

		self.on_log_stdout = lambda *args, **kwargs: None
		"""Callback for stdout output"""

		self.on_log_stderr = lambda *args, **kwargs: None
		"""Callback for stderr output"""