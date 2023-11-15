    def commands(self):
        cmd = ui.Subcommand('lyrics', help='fetch song lyrics')
        cmd.parser.add_option(
            u'-p', u'--print', dest='printlyr',
            action='store_true', default=False,
            help=u'print lyrics to console',
        )
        cmd.parser.add_option(
            u'-r', u'--write-rest', dest='writerest',
            action='store', default=None, metavar='dir',
            help=u'write lyrics to given directory as ReST files',
        )
        cmd.parser.add_option(
            u'-f', u'--force', dest='force_refetch',
            action='store_true', default=False,
            help=u'always re-download lyrics',
        )
        cmd.parser.add_option(
            u'-l', u'--local', dest='local_only',
            action='store_true', default=False,
            help=u'do not fetch missing lyrics',
        )

        def func(lib, opts, args):
            # The "write to files" option corresponds to the
            # import_write config value.
            write = ui.should_write()
            if opts.writerest:
                self.writerest_indexes(opts.writerest)
            for item in lib.items(ui.decargs(args)):
                if not opts.local_only and not self.config['local']:
                    self.fetch_item_lyrics(
                        lib, item, write,
                        opts.force_refetch or self.config['force'],
                    )
                if item.lyrics:
                    if opts.printlyr:
                        ui.print_(item.lyrics)
                    if opts.writerest:
                        self.writerest(opts.writerest, item)
            if opts.writerest:
                # flush last artist
                self.writerest(opts.writerest, None)
                ui.print_(u'ReST files generated. to build, use one of:')
                ui.print_(u'  sphinx-build -b html %s _build/html'
                          % opts.writerest)
                ui.print_(u'  sphinx-build -b epub %s _build/epub'
                          % opts.writerest)
                ui.print_((u'  sphinx-build -b latex %s _build/latex '
                           u'&& make -C _build/latex all-pdf')
                          % opts.writerest)
        cmd.func = func
        return [cmd]