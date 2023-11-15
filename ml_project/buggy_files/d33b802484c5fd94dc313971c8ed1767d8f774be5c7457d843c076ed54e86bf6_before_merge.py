def deleteTimelapse(filename):
	if util.is_allowed_file(filename, ["mpg"]):
		timelapse_folder = settings().getBaseFolder("timelapse")
		full_path = os.path.realpath(os.path.join(timelapse_folder, filename))
		if full_path.startswith(timelapse_folder) and os.path.exists(full_path):
			os.remove(full_path)
	return getTimelapseData()