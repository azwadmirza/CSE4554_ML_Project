    def display(self, msg=None, pos=None,
                # additional signals
                close=False, bar_style=None):
        # Note: contrary to native tqdm, msg='' does NOT clear bar
        # goal is to keep all infos if error happens so user knows
        # at which iteration the loop failed.

        # Clear previous output (really necessary?)
        # clear_output(wait=1)

        # Update description
        if self.desc:
            pbar.description = self.desc
            self.desc = None  # trick to place description before the bar
            if IPYW >= 7:
                pbar.style.description_width = 'initial'

        if not msg and not close:
            msg = self.__repr__()

        pbar, ptext = self.container.children

        # Get current iteration value from format_meter string
        if self.total:
            # n = None
            if msg:
                npos = msg.find(r'/|/')  # cause we use bar_format=r'{n}|...'
                # Check that n can be found in msg (else n > total)
                if npos >= 0:
                    n = float(msg[:npos])  # get n from string
                    msg = msg[npos + 3:]  # remove from string

                    # Update bar with current n value
                    if n is not None:
                        pbar.value = n

        # Print stats
        if msg:  # never clear the bar (signal: msg='')
            msg = msg.replace('||', '')  # remove inesthetical pipes
            msg = escape(msg)  # html escape special characters (like '?')
            ptext.value = msg

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