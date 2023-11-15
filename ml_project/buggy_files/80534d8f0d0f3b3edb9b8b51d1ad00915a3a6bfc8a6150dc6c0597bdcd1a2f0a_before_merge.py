    def restart(self):
        argv = [sys.executable] + sys.argv
        if '--no-spawn' not in argv:
            argv.append('--no-spawn')
        buf = io.BytesIO()
        try:
            pickle.dump(QtileState(self), buf, protocol=0)
        except:  # noqa: E722
            logger.error("Unable to pickle qtile state")
        argv = [s for s in argv if not s.startswith('--with-state')]
        argv.append('--with-state=' + buf.getvalue().decode())
        self._restart = (sys.executable, argv)
        self.stop()