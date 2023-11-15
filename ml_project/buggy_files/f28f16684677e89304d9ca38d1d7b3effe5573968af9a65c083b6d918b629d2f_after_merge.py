def delete_old_unrendered_timelapses():
	global _cleanup_lock

	basedir = settings().getBaseFolder("timelapse_tmp")
	clean_after_days = settings().getInt(["webcam", "cleanTmpAfterDays"])
	cutoff = time.time() - clean_after_days * 24 * 60 * 60

	prefixes_to_clean = []

	with _cleanup_lock:
		for filename in os.listdir(basedir):
			try:
				path = os.path.join(basedir, filename)

				prefix = _extract_prefix(filename)
				if prefix is None:
					# might be an old tmp_00000.jpg kinda frame. we can't
					# render those easily anymore, so delete that stuff
					if _old_capture_format_re.match(filename):
						os.remove(path)
					continue

				if prefix in prefixes_to_clean:
					continue

				if os.path.getmtime(path) < cutoff:
					prefixes_to_clean.append(prefix)
			except:
				if logging.getLogger(__name__).isEnabledFor(logging.DEBUG):
					logging.getLogger(__name__).exception("Error while processing file {} during cleanup".format(filename))

		for prefix in prefixes_to_clean:
			delete_unrendered_timelapse(prefix)
			logging.getLogger(__name__).info("Deleted old unrendered timelapse {}".format(prefix))