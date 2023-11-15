	def __init__(self, key, location, instance, name=None, version=None, description=None, author=None, url=None, license=None):
		self.key = key
		self.location = location
		self.instance = instance
		self.origin = None
		self.enabled = True
		self.blacklisted = False
		self.forced_disabled = False
		self.bundled = False
		self.loaded = False
		self.managable = True
		self.needs_restart = False

		self._name = name
		self._version = version
		self._description = description
		self._author = author
		self._url = url
		self._license = license