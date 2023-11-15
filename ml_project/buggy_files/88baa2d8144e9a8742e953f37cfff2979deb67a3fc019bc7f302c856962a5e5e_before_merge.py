def check_release_on_github(app):
	# Check if repo remote is on github
	from subprocess import CalledProcessError
	try:
		remote_url = subprocess.check_output("cd ../apps/{} && git ls-remote --get-url".format(app), shell=True).decode()
	except CalledProcessError:
		# Passing this since some apps may not have git initializaed in them
		return None

	if isinstance(remote_url, bytes):
		remote_url = remote_url.decode()

	if "github.com" not in remote_url:
		return None

	# Get latest version from github
	if 'https' not in remote_url:
		return None

	org_name = remote_url.split('/')[3]
	r = requests.get('https://api.github.com/repos/{}/{}/releases'.format(org_name, app))
	if r.ok:
		lastest_non_beta_release = parse_latest_non_beta_release(r.json())
		return Version(lastest_non_beta_release), org_name
	# In case of an improper response or if there are no releases
	return None