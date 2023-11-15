    def spawn_install_wheel(self, wheel, install_dir, compile=False, cache=None, target=None):

        target = target or DistributionTarget.current()

        install_cmd = [
            "install",
            "--no-deps",
            "--no-index",
            "--only-binary",
            ":all:",
            "--target",
            install_dir,
        ]

        interpreter = target.get_interpreter()
        if target.is_foreign:
            if compile:
                raise ValueError(
                    "Cannot compile bytecode for {} using {} because the wheel has a foreign "
                    "platform.".format(wheel, interpreter)
                )

            # We're installing a wheel for a foreign platform. This is just an unpacking operation though;
            # so we don't actually need to perform it with a target platform compatible interpreter.
            install_cmd.append("--ignore-requires-python")

        install_cmd.append("--compile" if compile else "--no-compile")
        install_cmd.append(wheel)
        return self._spawn_pip_isolated(install_cmd, cache=cache, interpreter=interpreter)