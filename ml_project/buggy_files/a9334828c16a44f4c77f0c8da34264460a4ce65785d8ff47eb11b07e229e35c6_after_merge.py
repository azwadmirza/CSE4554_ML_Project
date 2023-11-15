    def finish(self):
        # type: () -> None
        I18nBuilder.finish(self)
        data = dict(
            version = self.config.version,
            copyright = self.config.copyright,
            project = self.config.project,
            ctime = datetime.fromtimestamp(
                timestamp, ltz).strftime('%Y-%m-%d %H:%M%z'),
        )
        for textdomain, catalog in status_iterator(iteritems(self.catalogs),  # type: ignore
                                                   "writing message catalogs... ",
                                                   "darkgreen", len(self.catalogs),
                                                   self.app.verbosity,
                                                   lambda textdomain__: textdomain__[0]):
            # noop if config.gettext_compact is set
            ensuredir(path.join(self.outdir, path.dirname(textdomain)))

            pofn = path.join(self.outdir, textdomain + '.pot')
            output = StringIO()
            output.write(POHEADER % data)  # type: ignore

            for message in catalog.messages:
                positions = catalog.metadata[message]

                if self.config.gettext_location:
                    # generate "#: file1:line1\n#: file2:line2 ..."
                    output.write("#: %s\n" % "\n#: ".join(  # type: ignore
                        "%s:%s" % (canon_path(relpath(source, self.outdir)), line)
                        for source, line, _ in positions))
                if self.config.gettext_uuid:
                    # generate "# uuid1\n# uuid2\n ..."
                    output.write("# %s\n" % "\n# ".join(  # type: ignore
                        uid for _, _, uid in positions))

                # message contains *one* line of text ready for translation
                message = message.replace('\\', r'\\'). \
                    replace('"', r'\"'). \
                    replace('\n', '\\n"\n"')
                output.write('msgid "%s"\nmsgstr ""\n\n' % message)  # type: ignore

            content = output.getvalue()

            if should_write(pofn, content):
                with open(pofn, 'w', encoding='utf-8') as pofile:  # type: ignore
                    pofile.write(content)