    def translate_desktop(self, args):
        messages_file = os.path.join(args.translations_dir, 'desktop.pot')

        if args.extract_update:
            sources = args.sources.split(',')
            k = {'_cwd': args.translations_dir}
            xgettext(
                "--output=desktop.pot",
                "--language=Desktop",
                "--keyword",
                "--keyword=Name",
                "--package-version", args.version,
                "--msgid-bugs-address=securedrop@freedom.press",
                "--copyright-holder=Freedom of the Press Foundation",
                *sources,
                **k)
            sed('-i', '-e', '/^"POT-Creation-Date/d', messages_file, **k)

            if self.file_is_modified(messages_file):
                for f in os.listdir(args.translations_dir):
                    if not f.endswith('.po'):
                        continue
                    po_file = os.path.join(args.translations_dir, f)
                    msgmerge('--update', po_file, messages_file)
                log.warning("messages translations updated in " +
                            messages_file)
            else:
                log.warning("desktop translations are already up to date")

        if args.compile:
            pos = filter(lambda f: f.endswith('.po'),
                         os.listdir(args.translations_dir))
            linguas = map(lambda l: l[:-3], pos)
            content = "\n".join(linguas) + "\n"
            open(join(args.translations_dir, 'LINGUAS'), 'w').write(content)

            for source in args.sources.split(','):
                target = source.rstrip('.in')
                msgfmt('--desktop',
                       '--template', source,
                       '-o', target,
                       '-d', '.',
                       _cwd=args.translations_dir)