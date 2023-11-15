    def _getenvdata(self, reader, config):
        from_option = self.config.option.env
        from_environ = os.environ.get("TOXENV")
        from_config = reader.getstring("envlist", replace=False)

        env_list = []
        envlist_explicit = False
        if (from_option and "ALL" in from_option) or (
            not from_option and from_environ and "ALL" in from_environ.split(",")
        ):
            all_envs = self._getallenvs(reader)
        else:
            candidates = (
                (os.environ.get(PARALLEL_ENV_VAR_KEY_PRIVATE), True),
                (from_option, True),
                (from_environ, True),
                ("py" if self.config.option.devenv is not None else None, False),
                (from_config, False),
            )
            env_str, envlist_explicit = next(((i, e) for i, e in candidates if i), ([], False))
            env_list = _split_env(env_str)
            all_envs = self._getallenvs(reader, env_list)

        if not env_list:
            env_list = all_envs

        package_env = config.isolated_build_env
        if config.isolated_build is True and package_env in all_envs:
            all_envs.remove(package_env)

        if config.isolated_build is True and package_env in env_list:
            msg = "isolated_build_env {} cannot be part of envlist".format(package_env)
            raise tox.exception.ConfigError(msg)
        return env_list, all_envs, _split_env(from_config), envlist_explicit