	def average_total_rolling(self):
		if not self._count or self._count < self._rolling_window:
			return None
		else:
			return sum(self._totals) / len(self._totals)