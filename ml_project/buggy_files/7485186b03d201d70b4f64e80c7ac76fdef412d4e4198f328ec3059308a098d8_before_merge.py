    def restore_multiplexer_name(self):
        try:
            if 'TMUX' in os.environ:
                if self._tmux_automatic_rename:
                    check_output(['tmux', 'set-window-option',
                                  'automatic-rename',
                                  self._tmux_automatic_rename])
                else:
                    check_output(['tmux', 'set-window-option', '-u',
                                  'automatic-rename'])
                if self._tmux_title:
                    check_output(['tmux', 'rename-window', self._tmux_title])
            elif 'screen' in os.environ['TERM'] and self._screen_title:
                check_output(['screen', '-X', 'title', self._screen_title])
        except CalledProcessError:
            self.fm.notify("Could not restore window-name!", bad=True)