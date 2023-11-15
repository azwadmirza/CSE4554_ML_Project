    def _parse_packages(self, value):
        """Parses `packages` option value.

        :param value:
        :rtype: list
        """
        find_directives = ['find:', 'find_namespace:']
        trimmed_value = value.strip()

        if trimmed_value not in find_directives:
            return self._parse_list(value)

        findns = trimmed_value == find_directives[1]
        if findns and not PY3:
            raise DistutilsOptionError(
                'find_namespace: directive is unsupported on Python < 3.3')

        # Read function arguments from a dedicated section.
        find_kwargs = self.parse_section_packages__find(
            self.sections.get('packages.find', {}))

        if findns:
            from pex.third_party.setuptools import find_namespace_packages as find_packages
        else:
            from pex.third_party.setuptools import find_packages

        return find_packages(**find_kwargs)