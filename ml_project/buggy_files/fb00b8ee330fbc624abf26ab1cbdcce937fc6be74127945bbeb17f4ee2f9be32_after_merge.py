	def f(movie):
		global current_render_job
		global _job_lock
		with _job_lock:
			current_render_job = None