    def _save(self):
        """
        Save config into the associated .ini file
        """
        # See Issue 1086 and 1242 for background on why this
        # method contains all the exception handling.
        fname = self.filename()

        def _write_file(fname):
            if PY2:
                # Python 2
                with codecs.open(fname, 'w', encoding='utf-8') as configfile:
                    self._write(configfile)
            else:
                # Python 3
                with open(fname, 'w', encoding='utf-8') as configfile:
                    self.write(configfile)

        try:  # the "easy" way
            _write_file(fname)
        except IOError:
            try:  # the "delete and sleep" way
                if osp.isfile(fname):
                    os.remove(fname)
                time.sleep(0.05)
                _write_file(fname)
            except Exception as e:
                print("Failed to write user configuration file.")  # spyder: test-skip
                print("Please submit a bug report.")  # spyder: test-skip
                raise(e)