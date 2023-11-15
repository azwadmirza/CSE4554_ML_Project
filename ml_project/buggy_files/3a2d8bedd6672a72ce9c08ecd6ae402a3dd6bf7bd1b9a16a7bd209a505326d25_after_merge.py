def _create_render_success_handler(name, gcode=None):
	def f(movie):
		delete_unrendered_timelapse(name)
		event_payload = {"gcode": gcode if gcode is not None else "unknown",
		                 "movie": movie,
		                 "movie_basename": os.path.basename(movie),
		                 "movie_prefix": name}
		eventManager().fire(Events.MOVIE_DONE, event_payload)
	return f