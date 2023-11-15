    def _replace_match(self, match):
        g = match.groupdict()
        sub_value = g["substitution_value"]
        if self.crossonly:
            if sub_value.startswith("["):
                return self._substitute_from_other_section(sub_value)
            # in crossonly we return all other hits verbatim
            start, end = match.span()
            return match.string[start:end]

        full_match = match.group(0)
        # ":" is swallowed by the regex, so the raw matched string is checked
        if full_match.startswith("{:"):
            if full_match != "{:}":
                raise tox.exception.ConfigError(
                    "Malformed substitution with prefix ':': {}".format(full_match),
                )

            return os.pathsep

        default_value = g["default_value"]
        if sub_value == "posargs":
            return self.reader.getposargs(default_value)

        sub_type = g["sub_type"]
        if sub_type == "posargs":
            if default_value:
                value = "{}:{}".format(sub_value, default_value)
            else:
                value = sub_value
            return self.reader.getposargs(value)

        if not sub_type and not sub_value:
            raise tox.exception.ConfigError(
                "Malformed substitution; no substitution type provided. "
                "If you were using `{}` for `os.pathsep`, please use `{:}`.",
            )

        if not sub_type and not default_value and sub_value == "/":
            return os.sep

        if sub_type == "env":
            return self._replace_env(sub_value, default_value)
        if sub_type == "tty":
            if is_interactive():
                return match.group("substitution_value")
            return match.group("default_value")
        if sub_type == "posargs":
            return self.reader.getposargs(sub_value)
        if sub_type is not None:
            raise tox.exception.ConfigError(
                "No support for the {} substitution type".format(sub_type),
            )
        return self._replace_substitution(sub_value)