    def _open_call(self):
        args = self._create_arguments()
        if is_win32:
            fargs = args
        else:
            fargs = subprocess.list2cmdline(args)
        log.debug(u"Calling: {0}".format(fargs))

        subprocess.call(maybe_encode(args, get_filesystem_encoding()),
                        stdout=self.stdout,
                        stderr=self.stderr)