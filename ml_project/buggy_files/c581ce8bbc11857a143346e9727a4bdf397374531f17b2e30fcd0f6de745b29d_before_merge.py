def get_python_version_string():
	from platform import python_version
	version_string = python_version()

	# Debian has the python version set to 2.7.15+ which is not PEP440 compliant (bug 914072)
	if version_string.endswith("+"):
		version_string = python_version[:-1]

	return version_string