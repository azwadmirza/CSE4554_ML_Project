    def _substitute_from_other_section(self, key):
        if key.startswith("[") and "]" in key:
            i = key.find("]")
            section, item = key[1:i], key[i + 1 :]
            cfg = self.reader._cfg
            if section in cfg and item in cfg[section]:
                if (section, item) in self.reader._subststack:
                    raise tox.exception.SubstitutionStackError(
                        "{} already in {}".format((section, item), self.reader._subststack),
                    )
                x = str(cfg[section][item])
                return self.reader._replace(
                    x,
                    name=item,
                    section_name=section,
                    crossonly=self.crossonly,
                )

        raise tox.exception.ConfigError("substitution key {!r} not found".format(key))