    def _substitute_environ(self):
        """
        Substitute environment variables into values.
        """
        d = {}
        for field in self.__fields__.values():
            if field.alt_alias:
                env_name = field.alias
            else:
                env_name = self.__config__.env_prefix + field.name.upper()
            env_var = os.getenv(env_name, None)
            if env_var:
                if _complex_field(field):
                    try:
                        env_var = json.loads(env_var)
                    except ValueError as e:
                        raise SettingsError(f'error parsing JSON for "{env_name}"') from e
                d[field.alias] = env_var
        return d