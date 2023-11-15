    def __init__(self, cache_dir):
        self.state = {}
        self.statefile_path = None

        # Try to load the existing state
        if cache_dir:
            self.statefile_path = os.path.join(cache_dir, "selfcheck.json")
            try:
                with open(self.statefile_path) as statefile:
                    self.state = json.load(statefile)[sys.prefix]
            except (IOError, ValueError, KeyError):
                # Explicitly suppressing exceptions, since we don't want to
                # error out if the cache file is invalid.
                pass