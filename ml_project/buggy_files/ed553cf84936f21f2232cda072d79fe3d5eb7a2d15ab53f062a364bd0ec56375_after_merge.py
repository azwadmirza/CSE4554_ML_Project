    def find_key(self, items, write=False):
        overwrite = self.config['overwrite'].get(bool)
        command = [self.config['bin'].as_str()]
        # The KeyFinder GUI program needs the -f flag before the path.
        # keyfinder-cli is similar, but just wants the path with no flag.
        if 'keyfinder-cli' not in os.path.basename(command[0]).lower():
            command.append('-f')

        for item in items:
            if item['initial_key'] and not overwrite:
                continue

            try:
                output = util.command_output(command + [util.syspath(
                                                        item.path)]).stdout
            except (subprocess.CalledProcessError, OSError) as exc:
                self._log.error(u'execution failed: {0}', exc)
                continue
            except UnicodeEncodeError:
                # Workaround for Python 2 Windows bug.
                # https://bugs.python.org/issue1759845
                self._log.error(u'execution failed for Unicode path: {0!r}',
                                item.path)
                continue

            try:
                key_raw = output.rsplit(None, 1)[-1]
            except IndexError:
                # Sometimes keyfinder-cli returns 0 but with no key, usually
                # when the file is silent or corrupt, so we log and skip.
                self._log.error(u'no key returned for path: {0}', item.path)
                continue

            try:
                key = util.text_string(key_raw)
            except UnicodeDecodeError:
                self._log.error(u'output is invalid UTF-8')
                continue

            item['initial_key'] = key
            self._log.info(u'added computed initial key {0} for {1}',
                           key, util.displayable_path(item.path))

            if write:
                item.try_write()
            item.store()