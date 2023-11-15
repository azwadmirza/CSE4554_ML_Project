		def __init__(self, duration):
			"""Initialize a timeout with given duration"""
			self.is_infinite = (duration is None)
			self.is_non_blocking = (duration == 0)
			self.duration = duration
			if duration is not None:
				self.target_time = monotonic.monotonic() + duration
			else:
				self.target_time = None