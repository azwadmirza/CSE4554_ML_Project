    def restart(self):
        argv = [sys.executable] + sys.argv
        if '--no-spawn' not in argv:
            argv.append('--no-spawn')
        state_file = os.path.join(tempfile.gettempdir(), "qtile-state")
        try:
            with open(state_file, 'wb') as f:
                pickle.dump(QtileState(self), f, protocol=0)
        except:  # noqa: E722
            logger.error("Unable to pickle qtile state")
        argv = [s for s in argv if not s.startswith('--with-state')]
        argv.append('--with-state=' + state_file)
        self._restart = (sys.executable, argv)
        self.stop()