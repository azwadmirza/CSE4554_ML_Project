    def _replace(self, value, name=None, section_name=None, crossonly=False):
        if '{' not in value:
            return value

        section_name = section_name if section_name else self.section_name
        self._subststack.append((section_name, name))
        try:
            return Replacer(self, crossonly=crossonly).do_replace(value)
        finally:
            assert self._subststack.pop() == (section_name, name)