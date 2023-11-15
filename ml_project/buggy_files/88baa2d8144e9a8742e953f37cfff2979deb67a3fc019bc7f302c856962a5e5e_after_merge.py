def check_release_on_github(app: str):
	"""
	Check the latest release for a given Frappe application hosted on Github.

	Args:
		app (str): The name of the Frappe application.

	Returns:
		tuple(Version, str): The semantic version object of the latest release and the
			organization name, if the application exists, otherwise None.
	"""

	from giturlparse import parse
	from giturlparse.parser import ParserError

	try:
		# Check if repo remote is on github
		remote_url = subprocess.check_output("cd ../apps/{} && git ls-remote --get-url".format(app), shell=True)
	except subprocess.CalledProcessError:
		# Passing this since some apps may not have git initialized in them
		return

	if isinstance(remote_url, bytes):
		remote_url = remote_url.decode()

	try:
		parsed_url = parse(remote_url)
	except ParserError:
		# Invalid URL
		return

	if parsed_url.resource != "github.com":
		return

	owner = parsed_url.owner
	repo = parsed_url.name

	# Get latest version from GitHub
	r = requests.get(f"https://api.github.com/repos/{owner}/{repo}/releases")
	if r.ok:
		latest_non_beta_release = parse_latest_non_beta_release(r.json())
		if latest_non_beta_release:
			return Version(latest_non_beta_release), owner