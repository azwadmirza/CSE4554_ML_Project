    def refresh(self, inicontents=None):
        if inicontents is None:
            try:
                with salt.utils.files.fopen(self.name) as rfh:
                    inicontents = salt.utils.stringutils.to_unicode(rfh.read())
            except (OSError, IOError) as exc:
                if __opts__['test'] is False:
                    raise CommandExecutionError(
                        "Unable to open file '{0}'. "
                        "Exception: {1}".format(self.name, exc)
                    )
        if not inicontents:
            return
        # Remove anything left behind from a previous run.
        self.clear()

        inicontents = INI_REGX.split(inicontents)
        inicontents.reverse()
        # Pop anything defined outside of a section (ie. at the top of
        # the ini file).
        super(_Ini, self).refresh(inicontents.pop())
        for section_name, sect_ini in self._gen_tuples(inicontents):
            sect_obj = _Section(
                section_name, sect_ini, separator=self.sep
            )
            sect_obj.refresh()
            self.update({sect_obj.name: sect_obj})