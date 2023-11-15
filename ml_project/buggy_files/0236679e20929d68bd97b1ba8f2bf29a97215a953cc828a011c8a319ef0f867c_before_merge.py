    def files(self, only_unlocked=False):
        """Find and return the history files. Optionally locked files may be
        excluded.

        This is sorted by the last closed time. Returns a list of (timestamp,
        file) tuples.
        """
        _ = self  # this could be a function but is intimate to this class
        # pylint: disable=no-member
        xdd = os.path.abspath(builtins.__xonsh_env__.get('XONSH_DATA_DIR'))
        fs = [f for f in iglob(os.path.join(xdd, 'xonsh-*.json'))]
        files = []
        for f in fs:
            try:
                lj = lazyjson.LazyJSON(f, reopen=False)
                if only_unlocked and lj['locked']:
                    continue
                # info: closing timestamp, number of commands, filename
                files.append((lj['ts'][1] or time.time(), 
                              len(lj.sizes['cmds']) - 1, 
                              f))
                lj.close()
            except (IOError, OSError, ValueError):
                continue
        files.sort()
        return files