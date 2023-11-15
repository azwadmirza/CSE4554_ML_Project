        def func(lib, opts, args):
            # The "write to files" option corresponds to the
            # import_write config value.
            write = ui.should_write()
            if opts.writerest:
                self.writerest_indexes(opts.writerest)
            items = lib.items(ui.decargs(args))
            for item in items:
                if not opts.local_only and not self.config['local']:
                    self.fetch_item_lyrics(
                        lib, item, write,
                        opts.force_refetch or self.config['force'],
                    )
                if item.lyrics:
                    if opts.printlyr:
                        ui.print_(item.lyrics)
                    if opts.writerest:
                        self.appendrest(opts.writerest, item)
            if opts.writerest and items:
                # flush last artist & write to ReST
                self.writerest(opts.writerest)
                ui.print_(u'ReST files generated. to build, use one of:')
                ui.print_(u'  sphinx-build -b html %s _build/html'
                          % opts.writerest)
                ui.print_(u'  sphinx-build -b epub %s _build/epub'
                          % opts.writerest)
                ui.print_((u'  sphinx-build -b latex %s _build/latex '
                           u'&& make -C _build/latex all-pdf')
                          % opts.writerest)