    def _spawn_pip_isolated(
        self,
        args,  # type: List[str]
        env=None,  # type: Optional[Mapping[str, str]]
        cache=None,  # type: Optional[str]
        interpreter=None,  # type: Optional[PythonInterpreter]
    ):
        # type: (...) -> Job
        pip_args = [
            # We vendor the version of pip we want so pip should never check for updates.
            "--disable-pip-version-check",
            # Don't read pip configuration files like `~/.config/pip/pip.conf`.
            "--isolated",
            # If we want to warn about a version of python we support, we should do it, not pip.
            "--no-python-version-warning",
            # If pip encounters a duplicate file path during its operations we don't want it to prompt
            # and we'd also like to know about this since it should never occur. We leverage the pip
            # global option:
            # --exists-action <action>
            #   Default action when a path already exists: (s)witch, (i)gnore, (w)ipe, (b)ackup, (a)bort.
            "--exists-action",
            "a",
        ]

        # The max pip verbosity is -vvv and for pex it's -vvvvvvvvv; so we scale down by a factor of 3.

        # We cast to work around the current awkward state of `Variables` which can only return
        # `None` in a non-production states.
        # TODO(John Sirois): https://github.com/pantsbuild/pex/issues/1059
        pex_verbosity = cast(int, ENV.PEX_VERBOSE)
        pip_verbosity = pex_verbosity // 3
        if pip_verbosity > 0:
            pip_args.append("-{}".format("v" * pip_verbosity))
        else:
            pip_args.append("-q")

        if cache:
            pip_args.extend(["--cache-dir", cache])
        else:
            pip_args.append("--no-cache-dir")

        command = pip_args + args

        # We cast to work around the current awkward state of `Variables` which can only return
        # `None` in a non-production states.
        # TODO(John Sirois): https://github.com/pantsbuild/pex/issues/1059
        pex_root = cast(str, ENV.PEX_ROOT)
        with ENV.strip().patch(
            PEX_ROOT=cache or pex_root, PEX_VERBOSE=str(pex_verbosity), **(env or {})
        ) as env:
            # Guard against API calls from environment with ambient PYTHONPATH preventing pip PEX
            # bootstrapping. See: https://github.com/pantsbuild/pex/issues/892
            pythonpath = env.pop("PYTHONPATH", None)
            if pythonpath:
                TRACER.log(
                    "Scrubbed PYTHONPATH={} from the pip PEX environment.".format(pythonpath), V=3
                )

            from pex.pex import PEX

            pip = PEX(pex=self._pip_pex_path, interpreter=interpreter)
            return Job(
                command=pip.cmdline(command), process=pip.run(args=command, env=env, blocking=False)
            )