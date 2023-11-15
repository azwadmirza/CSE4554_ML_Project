	def set_actual_dates(self):
		self.actual_start_date = None
		self.actual_end_date = None
		if self.get("operations"):
			self.actual_start_date = min([d.actual_start_time for d in self.get("operations") if d.actual_start_time])
			self.actual_end_date = max([d.actual_end_time for d in self.get("operations") if d.actual_end_time])