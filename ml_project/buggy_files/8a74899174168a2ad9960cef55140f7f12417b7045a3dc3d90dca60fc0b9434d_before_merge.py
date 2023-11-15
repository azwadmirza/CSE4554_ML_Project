    def handle_multiplexer(self):
        if self.settings.update_tmux_title:
            if 'TMUX' in os.environ:
                # Stores the automatic-rename setting
                # prints out a warning if the allow-rename in tmux is not set
                tmux_allow_rename = check_output(
                    ['tmux', 'show-window-options', '-v',
                     'allow-rename']).strip()
                if tmux_allow_rename == 'off':
                    self.fm.notify('Warning: allow-rename not set in Tmux!',
                                   bad=True)
                elif self._tmux_title is None:
                    self._tmux_title = check_output(
                        ['tmux', 'display-message', '-p', '#W']).strip()
                else:
                    try:
                        self._tmux_automatic_rename = check_output(
                            ['tmux', 'show-window-options', '-v',
                             'automatic-rename']).strip()
                        if self._tmux_automatic_rename == 'on':
                            check_output(['tmux', 'set-window-option',
                                          'automatic-rename', 'off'])
                    except CalledProcessError:
                        pass
            elif 'screen' in os.environ['TERM'] and self._screen_title is None:
                # Stores the screen window name before renaming it
                # gives out a warning if $TERM is not "screen"
                try:
                    self._screen_title = check_output(
                        ['screen', '-Q', 'title'], shell=True).strip()
                except CalledProcessError:
                    self._screen_title = None

            sys.stdout.write("\033kranger\033\\")
            sys.stdout.flush()