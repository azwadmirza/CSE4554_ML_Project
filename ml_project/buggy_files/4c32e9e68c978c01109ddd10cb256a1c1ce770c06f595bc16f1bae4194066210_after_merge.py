	def f(movie):
		delete_unrendered_timelapse(name)
		event_payload = {"gcode": gcode if gcode is not None else "unknown",
		                 "movie": movie,
		                 "movie_basename": os.path.basename(movie)}
		eventManager().fire(Events.MOVIE_DONE, event_payload)