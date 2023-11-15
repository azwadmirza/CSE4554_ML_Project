    def setup_cache(self):
        if not self.enabled:
            return

        # create the logfile to start with
        with open(self.dump_fn, 'w') as f:
            json.dump({}, f, indent=2)