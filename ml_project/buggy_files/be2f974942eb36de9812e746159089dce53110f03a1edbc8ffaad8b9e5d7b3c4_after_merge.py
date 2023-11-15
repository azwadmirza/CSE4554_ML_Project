    def _replace(self, value, name=None, section_name=None, crossonly=False):
        if '{' not in value:
            return value

        section_name = section_name if section_name else self.section_name
        self._subststack.append((section_name, name))
        try:
            replaced = Replacer(self, crossonly=crossonly).do_replace(value)
            assert self._subststack.pop() == (section_name, name)
        except tox.exception.MissingSubstitution:
            if not section_name.startswith(testenvprefix):
                raise tox.exception.ConfigError(
                    "substitution env:%r: unknown or recursive definition in "
                    "section %r." % (value, section_name))
            raise
        return replaced