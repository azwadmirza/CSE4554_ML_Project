def cleanup_files(scan_id):
	print_info("Cleaning up files for %s" % scan_id)
	for file in glob.glob("data/*."+scan_id+".*"):
		os.remove(file)