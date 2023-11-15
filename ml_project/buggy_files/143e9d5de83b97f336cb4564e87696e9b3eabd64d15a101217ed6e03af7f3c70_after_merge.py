	def average_distance(self):
		if not self._count or self._count < self._rolling_window + 1 or not len(self._distances):
			return None
		else:
			return sum(self._distances) / len(self._distances)