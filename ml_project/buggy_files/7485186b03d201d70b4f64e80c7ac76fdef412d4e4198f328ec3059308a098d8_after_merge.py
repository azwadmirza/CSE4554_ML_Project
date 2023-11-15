    def restore_multiplexer_name(self):
        if self._multiplexer_title:
            try:
                if _in_tmux():
                    if self._tmux_automatic_rename:
                        check_output(['tmux', 'set-window-option',
                                      'automatic-rename',
                                      self._tmux_automatic_rename])
                    else:
                        check_output(['tmux', 'set-window-option', '-u',
                                      'automatic-rename'])
            except CalledProcessError:
                self.fm.notify("Could not restore multiplexer window name!",
                               bad=True)

            sys.stdout.write("\033k{}\033\\".format(self._multiplexer_title))
            sys.stdout.flush()