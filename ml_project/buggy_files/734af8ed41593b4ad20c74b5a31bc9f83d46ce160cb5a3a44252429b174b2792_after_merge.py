    def passenv(testenv_config, value):
        # Flatten the list to deal with space-separated values.
        value = list(itertools.chain.from_iterable([x.split(" ") for x in value]))

        passenv = {
            "PATH",
            "PIP_INDEX_URL",
            "LANG",
            "LANGUAGE",
            "LD_LIBRARY_PATH",
            "TOX_WORK_DIR",
            str(REPORTER_TIMESTAMP_ON_ENV),
            str(PARALLEL_ENV_VAR_KEY_PUBLIC),
        }

        # read in global passenv settings
        p = os.environ.get("TOX_TESTENV_PASSENV", None)
        if p is not None:
            env_values = [x for x in p.split() if x]
            value.extend(env_values)

        # we ensure that tmp directory settings are passed on
        # we could also set it to the per-venv "envtmpdir"
        # but this leads to very long paths when run with jenkins
        # so we just pass it on by default for now.
        if tox.INFO.IS_WIN:
            passenv.add("SYSTEMDRIVE")  # needed for pip6
            passenv.add("SYSTEMROOT")  # needed for python's crypto module
            passenv.add("PATHEXT")  # needed for discovering executables
            passenv.add("COMSPEC")  # needed for distutils cygwincompiler
            passenv.add("TEMP")
            passenv.add("TMP")
            # for `multiprocessing.cpu_count()` on Windows (prior to Python 3.4).
            passenv.add("NUMBER_OF_PROCESSORS")
            passenv.add("PROCESSOR_ARCHITECTURE")  # platform.machine()
            passenv.add("USERPROFILE")  # needed for `os.path.expanduser()`
            passenv.add("MSYSTEM")  # fixes #429
        else:
            passenv.add("TMPDIR")
        for spec in value:
            for name in os.environ:
                if fnmatchcase(name.upper(), spec.upper()):
                    passenv.add(name)
        return passenv