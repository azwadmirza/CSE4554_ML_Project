    def _replace_env(self, match):
        envkey = match.group('substitution_value')
        if not envkey:
            raise tox.exception.ConfigError('env: requires an environment variable name')
        default = match.group('default_value')
        envvalue = self.reader.get_environ_value(envkey)
        if envvalue is not None:
            return envvalue
        if default is not None:
            return default
        raise tox.exception.MissingSubstitution(envkey)