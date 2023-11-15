    def global_matches(self, text):
        """Compute matches when text is a simple name.

        Return a list of all keywords, built-in functions and names currently
        defined in self.namespace or self.global_namespace that match.

        """
        #print 'Completer->global_matches, txt=%r' % text # dbg
        matches = []
        match_append = matches.append
        n = len(text)
        for lst in [keyword.kwlist,
                    builtin_mod.__dict__.keys(),
                    self.namespace.keys(),
                    self.global_namespace.keys()]:
            for word in lst:
                if word[:n] == text and word != "__builtins__":
                    match_append(word)
        return [cast_unicode_py2(m) for m in matches]