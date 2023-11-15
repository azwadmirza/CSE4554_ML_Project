    def spawn_build_wheels(
        self,
        distributions,
        wheel_dir,
        interpreter=None,
        indexes=None,
        find_links=None,
        network_configuration=None,
        cache=None,
    ):

        wheel_cmd = ["wheel", "--no-deps", "--wheel-dir", wheel_dir]

        # If the build is PEP-517 compliant it may need to resolve build requirements.
        wheel_cmd.extend(
            self._calculate_package_index_args(
                indexes=indexes,
                find_links=find_links,
                network_configuration=network_configuration,
            )
        )
        env = dict(
            self._calculate_network_configuration_env(network_configuration=network_configuration)
        )

        wheel_cmd.extend(distributions)
        return self._spawn_pip_isolated(wheel_cmd, env=env, cache=cache, interpreter=interpreter)