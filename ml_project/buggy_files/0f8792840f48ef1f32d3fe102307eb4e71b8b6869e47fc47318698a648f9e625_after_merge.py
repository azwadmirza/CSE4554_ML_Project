    def getargvlist(cls, reader, value, replace=True, name=None):
        """Parse ``commands`` argvlist multiline string.

        :param SectionReader reader: reader to be used.
        :param str value: Content stored by key.

        :rtype: list[list[str]]
        :raise :class:`tox.exception.ConfigError`:
            line-continuation ends nowhere while resolving for specified section
        """
        commands = []
        current_command = ""
        for line in value.splitlines():
            line = line.rstrip()
            if not line:
                continue
            if line.endswith("\\"):
                current_command += " {}".format(line[:-1])
                continue
            current_command += line

            if is_section_substitution(current_command):
                replaced = reader._replace(current_command, crossonly=True, name=name)
                commands.extend(cls.getargvlist(reader, replaced, name=name))
            else:
                commands.append(cls.processcommand(reader, current_command, replace, name=name))
            current_command = ""
        else:
            if current_command:
                raise tox.exception.ConfigError(
                    "line-continuation ends nowhere while resolving for [{}] {}".format(
                        reader.section_name,
                        "commands",
                    ),
                )
        return commands