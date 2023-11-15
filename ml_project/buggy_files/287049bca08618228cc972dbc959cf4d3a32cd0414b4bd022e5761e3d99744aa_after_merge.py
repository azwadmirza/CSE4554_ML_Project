    def run(self):
        try:
            import readline
        except ImportError:
            return
        hist = builtins.__xonsh_history__
        while self.wait_for_gc and hist.gc.is_alive():
            time.sleep(0.011)  # gc sleeps for 0.01 secs, sleep a beat longer
        files = hist.gc.files()
        i = 1
        for _, _, f in files:
            try:
                lj = LazyJSON(f, reopen=False)
                for cmd in lj['cmds']:
                    inp = cmd['inp'].splitlines()
                    for line in inp:
                        if line == 'EOF':
                            continue
                        readline.add_history(line)
                        if RL_LIB is not None:
                            RL_LIB.history_set_pos(i)
                        i += 1
                lj.close()
            except (IOError, OSError, ValueError):
                continue