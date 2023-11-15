    def _create_arguments(self):
        if self.namedpipe:
            filename = self.namedpipe.path
        elif self.filename:
            filename = self.filename
        elif self.http:
            filename = self.http.url
        else:
            filename = "-"
        extra_args = []

        if self.title is not None:
            # vlc
            if self.player_name == "vlc":
                # see https://wiki.videolan.org/Documentation:Format_String/, allow escaping with \$
                self.title = self.title.replace("$", "$$").replace(r'\$$', "$")
                extra_args.extend(["--input-title-format", self.title])

            # mpv
            if self.player_name == "mpv":
                # see https://mpv.io/manual/stable/#property-expansion, allow escaping with \$, respect mpv's $>
                self.title = self._mpv_title_escape(self.title)
                extra_args.append("--title={}".format(self.title))

            # potplayer
            if self.player_name == "potplayer":
                if filename != "-":
                    # PotPlayer - About - Command Line
                    # You can specify titles for URLs by separating them with a backslash (\) at the end of URLs.
                    # eg. "http://...\title of this url"
                    self.title = self.title.replace('"', '')
                    filename = filename[:-1] + '\\' + self.title + filename[-1]

        args = self.args.format(filename=filename)
        cmd = self.cmd

        # player command
        if is_win32:
            eargs = maybe_decode(subprocess.list2cmdline(extra_args))
            # do not insert and extra " " when there are no extra_args
            return maybe_encode(u' '.join([cmd] + ([eargs] if eargs else []) + [args]),
                                encoding=get_filesystem_encoding())
        return shlex.split(cmd) + extra_args + shlex.split(args)