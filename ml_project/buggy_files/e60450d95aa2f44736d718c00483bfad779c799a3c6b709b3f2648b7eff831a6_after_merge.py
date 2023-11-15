    def _set_handler(self, log, output, fmt):
        # remove previous gunicorn log handler
        h = self._get_gunicorn_handler(log)
        if h:
            log.handlers.remove(h)

        if output is not None:
            if output == "-":
                h = logging.StreamHandler()
            else:
                util.check_is_writeable(output)
                h = logging.FileHandler(output)
                # make sure the user can reopen the file
                if not util.is_writable(h.baseFilename, self.cfg.user,
                        self.cfg.group):
                    os.chown(h.baseFilename, self.cfg.user, self.cfg.group)
            h.setFormatter(fmt)
            h._gunicorn = True
            log.addHandler(h)