    def handle_multiplexer(self):
        if (self.settings.update_tmux_title and not self._multiplexer_title):
            try:
                if _in_tmux():
                    # Stores the automatic-rename setting
                    # prints out a warning if allow-rename isn't set in tmux
                    try:
                        tmux_allow_rename = check_output(
                            ['tmux', 'show-window-options', '-v',
                             'allow-rename']).strip()
                    except CalledProcessError:
                        tmux_allow_rename = 'off'
                    if tmux_allow_rename == 'off':
                        self.fm.notify('Warning: allow-rename not set in Tmux!',
                                       bad=True)
                    else:
                        self._multiplexer_title = check_output(
                            ['tmux', 'display-message', '-p', '#W']).strip()
                        self._tmux_automatic_rename = check_output(
                            ['tmux', 'show-window-options', '-v',
                             'automatic-rename']).strip()
                        if self._tmux_automatic_rename == 'on':
                            check_output(['tmux', 'set-window-option',
                                          'automatic-rename', 'off'])
                elif _in_screen():
                    # Stores the screen window name before renaming it
                    # gives out a warning if $TERM is not "screen"
                    self._multiplexer_title = check_output(
                        ['screen', '-Q', 'title']).strip()
            except CalledProcessError:
                self.fm.notify("Couldn't access previous multiplexer window"
                               " name, won't be able to restore.",
                               bad=False)
            if not self._multiplexer_title:
                self._multiplexer_title = os.environ.get(
                    "SHELL",
                    "shell").split("/")[-1]

            sys.stdout.write("\033kranger\033\\")
            sys.stdout.flush()