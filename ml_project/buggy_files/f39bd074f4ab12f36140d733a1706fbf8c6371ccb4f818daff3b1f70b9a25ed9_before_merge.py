    def get_completions(self, document):
        """ Ask jedi to complete. """
        script = get_jedi_script_from_document(document, self.get_locals(), self.get_globals())

        if script:
            for c in script.completions():
                yield Completion(c.name_with_symbols, len(c.complete) - len(c.name_with_symbols),
                                 display=c.name_with_symbols)