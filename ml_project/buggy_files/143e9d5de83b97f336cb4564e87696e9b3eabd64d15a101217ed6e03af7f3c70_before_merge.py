	def average_distance(self):
		if not self._count or self._count < self._rolling_window + 1:
			return None
		else:
			return sum(self._distances) / len(self._distances)