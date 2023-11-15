def get_unrendered_timelapses():
	global _job_lock
	global current

	delete_old_unrendered_timelapses()

	basedir = settings().getBaseFolder("timelapse_tmp", check_writable=False)
	jobs = collections.defaultdict(lambda: dict(count=0, size=None, bytes=0, date=None, timestamp=None))

	for entry in scandir(basedir):
		if not fnmatch.fnmatch(entry.name, "*.jpg"):
			continue

		prefix = _extract_prefix(entry.name)
		if prefix is None:
			continue

		jobs[prefix]["count"] += 1
		jobs[prefix]["bytes"] += entry.stat().st_size
		if jobs[prefix]["timestamp"] is None or entry.stat().st_mtime < jobs[prefix]["timestamp"]:
			jobs[prefix]["timestamp"] = entry.stat().st_mtime

	with _job_lock:
		global current_render_job

		def finalize_fields(prefix, job):
			currently_recording = current is not None and current.prefix == prefix
			currently_rendering = current_render_job is not None and current_render_job["prefix"] == prefix

			job["size"] = util.get_formatted_size(job["bytes"])
			job["date"] = util.get_formatted_datetime(datetime.datetime.fromtimestamp(job["timestamp"]))
			job["recording"] = currently_recording
			job["rendering"] = currently_rendering
			job["processing"] = currently_recording or currently_rendering
			del job["timestamp"]

			return job

		return sorted([util.dict_merge(dict(name=key), finalize_fields(key, value)) for key, value in jobs.items()], key=lambda x: sv(x["name"]))