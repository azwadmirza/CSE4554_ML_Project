	def f(movie, returncode=255, stdout="Unknown error", stderr="Unknown error"):
		event_payload = {"gcode": gcode if gcode is not None else "unknown",
		                 "movie": movie,
		                 "movie_basename": os.path.basename(movie)}
		payload = dict(event_payload)
		payload.update(dict(returncode=returncode, error=stderr))
		eventManager().fire(Events.MOVIE_FAILED, payload)