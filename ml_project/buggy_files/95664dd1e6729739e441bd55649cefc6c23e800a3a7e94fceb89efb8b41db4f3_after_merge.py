    def gen_ini(self):
        yield '{0}[{1}]{0}'.format(os.linesep, self.name)
        sections_dict = OrderedDict()
        for name, value in six.iteritems(self):
            # Handle Comment Lines
            if COM_REGX.match(name):
                yield '{0}{1}'.format(value, os.linesep)
            # Handle Sections
            elif isinstance(value, _Section):
                sections_dict.update({name: value})
            # Key / Value pairs
            # Adds spaces between the separator
            else:
                yield '{0}{1}{2}{3}'.format(
                    name,
                    ' {0} '.format(self.sep) if self.sep != ' ' else self.sep,
                    value,
                    os.linesep
                )
        for name, value in six.iteritems(sections_dict):
            for line in value.gen_ini():
                yield line