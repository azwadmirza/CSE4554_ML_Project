    def get_completions(self, document):
        """ Ask jedi to complete. """
        script = get_jedi_script_from_document(document, self.get_locals(), self.get_globals())

        if script:
            try:
                completions = script.completions()
            except TypeError:
                # Issue #9: bad syntax causes completions() to fail in jedi.
                # https://github.com/jonathanslenders/python-prompt-toolkit/issues/9
                pass
            except UnicodeDecodeError:
                # Issue #43: UnicodeDecodeError on OpenBSD
                # https://github.com/jonathanslenders/python-prompt-toolkit/issues/43
                pass
            else:
                for c in completions:
                    yield Completion(c.name_with_symbols, len(c.complete) - len(c.name_with_symbols),
                                     display=c.name_with_symbols)