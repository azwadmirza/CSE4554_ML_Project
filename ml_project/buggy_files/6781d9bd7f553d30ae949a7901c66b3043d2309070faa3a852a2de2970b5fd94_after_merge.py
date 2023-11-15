async def find_pex_python(
    python_setup: PythonSetup,
    pex_runtime_env: PexRuntimeEnvironment,
    subprocess_env_vars: SubprocessEnvironmentVars,
) -> PexEnvironment:
    # PEX files are compatible with bootstrapping via Python 2.7 or Python 3.5+. The bootstrap
    # code will then re-exec itself if the underlying PEX user code needs a more specific python
    # interpreter. As such, we look for many Pythons usable by the PEX bootstrap code here for
    # maximum flexibility.
    all_python_binary_paths = await MultiGet(
        Get(
            BinaryPaths,
            BinaryPathRequest(
                search_path=python_setup.interpreter_search_paths,
                binary_name=binary_name,
                test=BinaryPathTest(
                    args=[
                        "-c",
                        # N.B.: The following code snippet must be compatible with Python 2.7 and
                        # Python 3.5+.
                        dedent(
                            """\
                            import sys

                            major, minor = sys.version_info[:2]
                            if (major, minor) == (2, 7) or (major == 3 and minor >= 5):
                                # Here we hash the underlying python interpreter executable to
                                # ensure we detect changes in the real interpreter that might
                                # otherwise be masked by pyenv shim scripts found on the search
                                # path. Naively, just printing out the full version_info would be
                                # enough, but that does not account for supported abi changes (e.g.:
                                # a pyenv switch from a py27mu interpreter to a py27m interpreter.
                                import hashlib
                                hasher = hashlib.sha256()
                                with open(sys.executable, "rb") as fp:
                                    # We pick 8192 for efficiency of reads and fingerprint updates
                                    # (writes) since it's a common OS buffer size and an even
                                    # multiple of the hash block size.
                                    for chunk in iter(lambda: fp.read(8192), b""):
                                        hasher.update(chunk)
                                sys.stdout.write(hasher.hexdigest())
                                sys.exit(0)
                            else:
                                sys.exit(1)
                            """
                        ),
                    ],
                    fingerprint_stdout=False,  # We already emit a usable fingerprint to stdout.
                ),
            ),
        )
        for binary_name in pex_runtime_env.bootstrap_interpreter_names
    )

    def first_python_binary() -> Optional[PythonExecutable]:
        for binary_paths in all_python_binary_paths:
            if binary_paths.first_path:
                return PythonExecutable(
                    path=binary_paths.first_path.path,
                    fingerprint=binary_paths.first_path.fingerprint,
                )
        return None

    return PexEnvironment(
        path=pex_runtime_env.path,
        interpreter_search_paths=tuple(python_setup.interpreter_search_paths),
        subprocess_environment_dict=subprocess_env_vars.vars,
        bootstrap_python=first_python_binary(),
    )