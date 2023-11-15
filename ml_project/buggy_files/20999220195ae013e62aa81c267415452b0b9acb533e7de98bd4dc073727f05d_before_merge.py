    def all_items(self, **kwargs):
        """
        Returns all history as found in XONSH_DATA_DIR.

        yield format: {'inp': cmd, 'rtn': 0, ...}
        """
        while self.gc and self.gc.is_alive():
            time.sleep(0.011)  # gc sleeps for 0.01 secs, sleep a beat longer
        for f in _xhj_get_history_files():
            try:
                json_file = xlj.LazyJSON(f, reopen=False)
            except ValueError:
                # Invalid json file
                continue
            commands = json_file.load()['cmds']
            for c in commands:
                yield {'inp': c['inp'].rstrip(), 'ts': c['ts'][0]}
        # all items should also include session items
        yield from self.items()