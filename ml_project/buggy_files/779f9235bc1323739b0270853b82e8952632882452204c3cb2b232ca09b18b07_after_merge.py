    def run(self):
        hist = builtins.__xonsh_history__
        buf = None
        ptkhist = self.ptkhist
        while self.wait_for_gc and hist.gc.is_alive():
            time.sleep(0.011)  # gc sleeps for 0.01 secs, sleep a beat longer
        files = hist.gc.files()
        for _, _, f in files:
            try:
                lj = lazyjson.LazyJSON(f, reopen=False)
                for cmd in lj['cmds']:
                    line = cmd['inp'].rstrip()
                    if line == 'EOF':
                        continue
                    if len(ptkhist) == 0 or line != ptkhist[-1]:
                        ptkhist.append(line)
                        if buf is None:
                            buf = self._buf()
                            if buf is None:
                                continue
                        buf.reset(initial_document=buf.document)
                lj.close()
            except (IOError, OSError, ValueError):
                continue