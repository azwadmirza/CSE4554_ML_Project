def _create_render_always_handler(name, gcode=None):
	def f(movie):
		global current_render_job
		global _job_lock
		with _job_lock:
			current_render_job = None
	return f