def delete_unrendered_timelapse(name):
	basedir = settings().getBaseFolder("timelapse_tmp")
	for filename in os.listdir(basedir):
		try:
			if fnmatch.fnmatch(filename, "{}*.jpg".format(name)):
				os.remove(os.path.join(basedir, filename))
		except:
			logging.getLogger(__name__).exception("Error while processing file {} during cleanup".format(filename))