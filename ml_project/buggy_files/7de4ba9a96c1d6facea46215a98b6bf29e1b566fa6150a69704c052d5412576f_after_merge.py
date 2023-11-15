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
                   - xterm256: Enforce xterm256 colors, regardless of TTYPE.
                   - noxterm256: Enforce no xterm256 color support, regardless of TTYPE.
                   - nocolor: Strip all Color, regardless of ansi/xterm256 setting.
                   - raw: Pass string through without any ansi processing
                        (i.e. include Evennia ansi markers but do not
                        convert them into ansi tokens)
                   - echo: Turn on/off line echo on the client. Turn
                        off line echo for client, for example for password.
                        Note that it must be actively turned back on again!

        """
        text = args[0] if args else ""
        if text is None:
            return
        text = to_str(text, force_string=True)

        # handle arguments
        options = kwargs.get("options", {})
        flags = self.protocol_flags
        xterm256 = options.get("xterm256", flags.get('XTERM256', False) if flags["TTYPE"] else True)
        useansi = options.get("ansi", flags.get('ANSI', False) if flags["TTYPE"] else True)
        raw = options.get("raw", flags.get("RAW", False))
        nocolor = options.get("nocolor", flags.get("NOCOLOR") or not (xterm256 or useansi))
        echo = options.get("echo", None)
        mxp = options.get("mxp", flags.get("MXP", False))
        screenreader = options.get("screenreader", flags.get("SCREENREADER", False))

        if screenreader:
            # screenreader mode cleans up output
            text = ansi.parse_ansi(text, strip_ansi=True, xterm256=False, mxp=False)
            text = _RE_SCREENREADER_REGEX.sub("", text)

        if options.get("send_prompt"):
            # send a prompt instead.
            prompt = text
            if not raw:
                # processing
                prompt = ansi.parse_ansi(_RE_N.sub("", prompt) + ("|n" if prompt[-1] != "|" else "||n"),
                                         strip_ansi=nocolor, xterm256=xterm256)
                if mxp:
                    prompt = mxp_parse(prompt)
            prompt = prompt.replace(IAC, IAC + IAC).replace('\n', '\r\n')
            prompt += IAC + GA
            self.transport.write(mccp_compress(self, prompt))
        else:
            if echo is not None:
                # turn on/off echo. Note that this is a bit turned around since we use
                # echo as if we are "turning off the client's echo" when telnet really
                # handles it the other way around.
                if echo:
                    # by telling the client that WE WON'T echo, the client knows
                    # that IT should echo. This is the expected behavior from
                    # our perspective.
                    self.transport.write(mccp_compress(self, IAC+WONT+ECHO))
                else:
                    # by telling the client that WE WILL echo, the client can
                    # safely turn OFF its OWN echo.
                    self.transport.write(mccp_compress(self, IAC+WILL+ECHO))
            if raw:
                # no processing
                self.sendLine(text)
                return
            else:
                # we need to make sure to kill the color at the end in order
                # to match the webclient output.
                linetosend = ansi.parse_ansi(_RE_N.sub("", text) + ("||n" if text.endswith("|") else "|n"),
                                             strip_ansi=nocolor, xterm256=xterm256, mxp=mxp)
                if mxp:
                    linetosend = mxp_parse(linetosend)
                self.sendLine(linetosend)