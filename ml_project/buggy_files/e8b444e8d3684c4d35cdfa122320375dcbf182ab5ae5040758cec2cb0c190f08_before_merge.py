	def __init__(self, job_type):
		self.stats_weighing_until = settings().getFloat(["estimation", "printTime", "statsWeighingUntil"])
		self.validity_range = settings().getFloat(["estimation", "printTime", "validityRange"])
		self.force_dumb_from_percent = settings().getFloat(["estimation", "printTime", "forceDumbFromPercent"])
		self.force_dumb_after_min = settings().getFloat(["estimation", "printTime", "forceDumbAfterMin"])

		threshold = None
		rolling_window = None
		countdown = None

		if job_type == "local" or job_type == "sdcard":
			# we are happy if the average of the estimates stays within 60s of the prior one
			threshold = settings().getFloat(["estimation", "printTime", "stableThreshold"])

			if job_type == "sdcard":
				# we are interesting in a rolling window of roughly the last 15s, so the number of entries has to be derived
				# by that divided by the sd status polling interval
				interval = settings().getFloat(["serial", "timeout", "sdStatus"])
				if interval <= 0:
					interval = 1.0
				rolling_window = 15 / interval

				# we are happy when one rolling window has been stable
				countdown = rolling_window

		self._data = TimeEstimationHelper(rolling_window=rolling_window, countdown=countdown, threshold=threshold)