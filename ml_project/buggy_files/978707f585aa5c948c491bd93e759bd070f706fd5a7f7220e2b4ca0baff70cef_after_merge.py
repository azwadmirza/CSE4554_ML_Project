def cleanup_files(scan_id):
	print_info("Cleaning up files for %s" % scan_id)
	if os.path.isdir("data/aquatone.%s" % scan_id):
		shutil.rmtree("data/aquatone.%s" % scan_id)
	for file in glob.glob("data/natlas."+scan_id+".*"):
		try:
			os.remove(file)
		except:
			print_err("Could not remove file %s" % file)