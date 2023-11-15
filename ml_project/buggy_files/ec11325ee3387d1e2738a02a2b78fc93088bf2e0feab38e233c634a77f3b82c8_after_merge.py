    def send_text(self, *args, **kwargs):
        """
        Send text data. This is an in-band telnet operation.

        Args:
            text (str): The first argument is always the text string to send. No other arguments
                are considered.
        Kwargs:
            options (dict): Send-option flags
                   - mxp: Enforce MXP link support.
                   - ansi: Enforce no ANSI colors.
                   - xterm256: Enforce xterm256 colors, regardless of TTYPE setting.
                   - nocolor: Strip all colors.
                   - raw: Pass string through without any ansi processing
                        (i.e. include Evennia ansi markers but do not
                        convert them into ansi tokens)
                   - echo: Turn on/off line echo on the client. Turn
                        off line echo for client, for example for password.
                        Note that it must be actively turned back on again!

        """
        # print "telnet.send_text", args,kwargs  # DEBUG
        text = args[0] if args else ""
        if text is None:
            return
        text = to_str(text, force_string=True)

        # handle arguments
        options = kwargs.get("options", {})
        flags = self.protocol_flags
        xterm256 = options.get("xterm256", flags.get('XTERM256', True))
        useansi = options.get("ansi", flags.get('ANSI', True))
        raw = options.get("raw", flags.get("RAW", False))
        nocolor = options.get("nocolor", flags.get("NOCOLOR") or not (xterm256 or useansi))
        # echo = options.get("echo", None)  # DEBUG
        screenreader = options.get("screenreader", flags.get("SCREENREADER", False))

        if screenreader:
            # screenreader mode cleans up output
            text = ansi.parse_ansi(text, strip_ansi=True, xterm256=False, mxp=False)
            text = _RE_SCREENREADER_REGEX.sub("", text)

        if raw:
            # no processing
            self.sendLine(text)
            return
        else:
            # we need to make sure to kill the color at the end in order
            # to match the webclient output.
            linetosend = ansi.parse_ansi(_RE_N.sub("", text) + ("||n" if text.endswith("|") else "|n"),
                                         strip_ansi=nocolor, xterm256=xterm256, mxp=False)
            self.sendLine(linetosend)