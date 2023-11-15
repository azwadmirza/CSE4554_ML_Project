    def __init__(self, cache_dir):
        self.statefile_path = os.path.join(cache_dir, "selfcheck.json")

        # Load the existing state
        try:
            with open(self.statefile_path) as statefile:
                self.state = json.load(statefile)[sys.prefix]
        except (IOError, ValueError, KeyError):
            self.state = {}