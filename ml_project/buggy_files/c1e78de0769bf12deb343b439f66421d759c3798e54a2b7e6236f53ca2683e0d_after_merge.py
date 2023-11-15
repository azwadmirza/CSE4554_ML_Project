def delete_unrendered_timelapse(name):
	global _cleanup_lock

	basedir = settings().getBaseFolder("timelapse_tmp")
	with _cleanup_lock:
		for filename in os.listdir(basedir):
			try:
				if fnmatch.fnmatch(filename, "{}*.jpg".format(name)):
					os.remove(os.path.join(basedir, filename))
			except:
				if logging.getLogger(__name__).isEnabledFor(logging.DEBUG):
					logging.getLogger(__name__).exception("Error while processing file {} during cleanup".format(filename))