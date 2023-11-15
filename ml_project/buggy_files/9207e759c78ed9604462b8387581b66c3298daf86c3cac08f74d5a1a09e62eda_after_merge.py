    def display(self, msg=None, pos=None,
                # additional signals
                close=False, bar_style=None):
        # Note: contrary to native tqdm, msg='' does NOT clear bar
        # goal is to keep all infos if error happens so user knows
        # at which iteration the loop failed.

        # Clear previous output (really necessary?)
        # clear_output(wait=1)

        if not msg and not close:
            msg = self.__repr__()

        pbar, ptext = self.container.children
        pbar.value = self.n

        if msg:
            # html escape special characters (like '&')
            if '<bar/>' in msg:
                left, right = map(escape, msg.split('<bar/>', 1))
            else:
                left, right = '', escape(msg)

            # remove inesthetical pipes
            if left and left[-1] == '|':
                left = left[:-1]
            if right and right[0] == '|':
                right = right[1:]

            # Update description
            pbar.description = left
            if IPYW >= 7:
                pbar.style.description_width = 'initial'

            # never clear the bar (signal: msg='')
            if right:
                ptext.value = right

        # Change bar style
        if bar_style:
            # Hack-ish way to avoid the danger bar_style being overridden by
            # success because the bar gets closed after the error...
            if not (pbar.bar_style == 'danger' and bar_style == 'success'):
                pbar.bar_style = bar_style

        # Special signal to close the bar
        if close and pbar.bar_style != 'danger':  # hide only if no error
            try:
                self.container.close()
            except AttributeError:
                self.container.visible = False