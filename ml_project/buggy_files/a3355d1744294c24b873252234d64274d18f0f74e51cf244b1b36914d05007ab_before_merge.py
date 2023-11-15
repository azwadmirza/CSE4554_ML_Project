    def _replace_env(self, match):
        envkey = match.group('substitution_value')
        if not envkey:
            raise tox.exception.ConfigError(
                'env: requires an environment variable name')

        default = match.group('default_value')

        envvalue = self.reader.get_environ_value(envkey)
        if envvalue is None:
            if default is None:
                raise tox.exception.ConfigError(
                    "substitution env:%r: unknown environment variable %r "
                    " or recursive definition." %
                    (envkey, envkey))
            return default
        return envvalue