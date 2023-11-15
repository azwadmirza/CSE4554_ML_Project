    def spawn_download_distributions(
        self,
        download_dir,
        requirements=None,
        requirement_files=None,
        constraint_files=None,
        allow_prereleases=False,
        transitive=True,
        target=None,
        indexes=None,
        find_links=None,
        network_configuration=None,
        cache=None,
        build=True,
        manylinux=None,
        use_wheel=True,
    ):

        target = target or DistributionTarget.current()

        platform = target.get_platform()
        if not use_wheel:
            if not build:
                raise ValueError(
                    "Cannot both ignore wheels (use_wheel=False) and refrain from building "
                    "distributions (build=False)."
                )
            elif target.is_foreign:
                raise ValueError(
                    "Cannot ignore wheels (use_wheel=False) when resolving for a foreign "
                    "platform: {}".format(platform)
                )

        download_cmd = ["download", "--dest", download_dir]
        package_index_options = self._calculate_package_index_options(
            indexes=indexes,
            find_links=find_links,
            network_configuration=network_configuration,
        )
        download_cmd.extend(package_index_options)

        if target.is_foreign:
            # We're either resolving for a different host / platform or a different interpreter for the
            # current platform that we have no access to; so we need to let pip know and not otherwise
            # pickup platform info from the interpreter we execute pip with.
            if manylinux and platform.platform.startswith("linux"):
                download_cmd.extend(
                    ["--platform", platform.platform.replace("linux", manylinux, 1)]
                )
            download_cmd.extend(["--platform", platform.platform])
            download_cmd.extend(["--implementation", platform.impl])
            download_cmd.extend(["--python-version", platform.version])
            download_cmd.extend(["--abi", platform.abi])

        if target.is_foreign or not build:
            download_cmd.extend(["--only-binary", ":all:"])

        if not use_wheel:
            download_cmd.extend(["--no-binary", ":all:"])

        if allow_prereleases:
            download_cmd.append("--pre")

        if not transitive:
            download_cmd.append("--no-deps")

        if requirement_files:
            for requirement_file in requirement_files:
                download_cmd.extend(["--requirement", requirement_file])

        if constraint_files:
            for constraint_file in constraint_files:
                download_cmd.extend(["--constraint", constraint_file])

        download_cmd.extend(requirements)

        return self._spawn_pip_isolated(
            download_cmd, cache=cache, interpreter=target.get_interpreter()
        )