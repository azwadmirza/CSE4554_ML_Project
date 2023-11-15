    def update_keyhint(self, modename, prefix):
        """Show hints for the given prefix (or hide if prefix is empty).

        Args:
            prefix: The current partial keystring.
        """
        countstr, prefix = re.fullmatch(r'(\d*)(.*)', prefix).groups()
        if not prefix:
            self._show_timer.stop()
            self.hide()
            return

        def blacklisted(keychain):
            return any(fnmatch.fnmatchcase(keychain, glob)
                       for glob in config.val.keyhint.blacklist)

        def takes_count(cmdstr):
            """Return true iff this command can take a count argument."""
            cmdname = cmdstr.split(' ')[0]
            cmd = cmdutils.cmd_dict.get(cmdname)
            return cmd and cmd.takes_count()

        bindings_dict = config.key_instance.get_bindings_for(modename)
        bindings = [(k, v) for (k, v) in sorted(bindings_dict.items())
                    if keyutils.KeySequence.parse(prefix).matches(k) and
                    not blacklisted(str(k)) and
                    (takes_count(v) or not countstr)]

        if not bindings:
            self._show_timer.stop()
            return

        # delay so a quickly typed keychain doesn't display hints
        self._show_timer.setInterval(config.val.keyhint.delay)
        self._show_timer.start()
        suffix_color = html.escape(config.val.colors.keyhint.suffix.fg)

        text = ''
        for seq, cmd in bindings:
            text += (
                "<tr>"
                "<td>{}</td>"
                "<td style='color: {}'>{}</td>"
                "<td style='padding-left: 2ex'>{}</td>"
                "</tr>"
            ).format(
                html.escape(prefix),
                suffix_color,
                html.escape(str(seq)[len(prefix):]),
                html.escape(cmd)
            )
        text = '<table>{}</table>'.format(text)

        self.setText(text)
        self.adjustSize()
        self.update_geometry.emit()