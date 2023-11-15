def tox_addoption(parser):
    parser.add_argument(
        "--version", action="store_true", help="report version information to stdout."
    )
    parser.add_argument("-h", "--help", action="store_true", help="show help about options")
    parser.add_argument(
        "--help-ini", "--hi", action="store_true", dest="helpini", help="show help about ini-names"
    )
    add_verbosity_commands(parser)
    parser.add_argument(
        "--showconfig",
        action="store_true",
        help="show live configuration (by default all env, with -l only default targets,"
        " specific via TOXENV/-e)",
    )
    parser.add_argument(
        "-l",
        "--listenvs",
        action="store_true",
        help="show list of test environments (with description if verbose)",
    )
    parser.add_argument(
        "-a",
        "--listenvs-all",
        action="store_true",
        help="show list of all defined environments (with description if verbose)",
    )
    parser.add_argument(
        "-c", dest="configfile", help="config file name or directory with 'tox.ini' file."
    )
    parser.add_argument(
        "-e",
        action="append",
        dest="env",
        metavar="envlist",
        help="work against specified environments (ALL selects all).",
    )
    parser.add_argument(
        "--devenv",
        metavar="ENVDIR",
        help=(
            "sets up a development environment at ENVDIR based on the env's tox "
            "configuration specified by `-e` (-e defaults to py)."
        ),
    )
    parser.add_argument("--notest", action="store_true", help="skip invoking test commands.")
    parser.add_argument(
        "--sdistonly", action="store_true", help="only perform the sdist packaging activity."
    )
    add_parallel_flags(parser)
    parser.add_argument(
        "--parallel--safe-build",
        action="store_true",
        dest="parallel_safe_build",
        help="(deprecated) ensure two tox builds can run in parallel "
        "(uses a lock file in the tox workdir with .lock extension)",
    )
    parser.add_argument(
        "--installpkg",
        metavar="PATH",
        help="use specified package for installation into venv, instead of creating an sdist.",
    )
    parser.add_argument(
        "--develop",
        action="store_true",
        help="install package in the venv using 'setup.py develop' via 'pip -e .'",
    )
    parser.add_argument(
        "-i",
        "--index-url",
        action="append",
        dest="indexurl",
        metavar="URL",
        help="set indexserver url (if URL is of form name=url set the "
        "url for the 'name' indexserver, specifically)",
    )
    parser.add_argument(
        "--pre",
        action="store_true",
        help="install pre-releases and development versions of dependencies. "
        "This will pass the --pre option to install_command "
        "(pip by default).",
    )
    parser.add_argument(
        "-r", "--recreate", action="store_true", help="force recreation of virtual environments"
    )
    parser.add_argument(
        "--result-json",
        dest="resultjson",
        metavar="PATH",
        help="write a json file with detailed information "
        "about all commands and results involved.",
    )

    # We choose 1 to 4294967295 because it is the range of PYTHONHASHSEED.
    parser.add_argument(
        "--hashseed",
        metavar="SEED",
        help="set PYTHONHASHSEED to SEED before running commands.  "
        "Defaults to a random integer in the range [1, 4294967295] "
        "([1, 1024] on Windows). "
        "Passing 'noset' suppresses this behavior.",
    )
    parser.add_argument(
        "--force-dep",
        action="append",
        metavar="REQ",
        help="Forces a certain version of one of the dependencies "
        "when configuring the virtual environment. REQ Examples "
        "'pytest<2.7' or 'django>=1.6'.",
    )
    parser.add_argument(
        "--sitepackages",
        action="store_true",
        help="override sitepackages setting to True in all envs",
    )
    parser.add_argument(
        "--alwayscopy", action="store_true", help="override alwayscopy setting to True in all envs"
    )

    cli_skip_missing_interpreter(parser)
    parser.add_argument("--workdir", metavar="PATH", help="tox working directory")

    parser.add_argument(
        "args", nargs="*", help="additional arguments available to command positional substitution"
    )

    def _set_envdir_from_devenv(testenv_config, value):
        if testenv_config.config.option.devenv is not None:
            return py.path.local(testenv_config.config.option.devenv)
        else:
            return value

    parser.add_testenv_attribute(
        name="envdir",
        type="path",
        default="{toxworkdir}/{envname}",
        help="set venv directory -- be very careful when changing this as tox "
        "will remove this directory when recreating an environment",
        postprocess=_set_envdir_from_devenv,
    )

    # add various core venv interpreter attributes
    def setenv(testenv_config, value):
        setenv = value
        config = testenv_config.config
        if "PYTHONHASHSEED" not in setenv and config.hashseed is not None:
            setenv["PYTHONHASHSEED"] = config.hashseed

        setenv["TOX_ENV_NAME"] = str(testenv_config.envname)
        setenv["TOX_ENV_DIR"] = str(testenv_config.envdir)
        return setenv

    parser.add_testenv_attribute(
        name="setenv",
        type="dict_setenv",
        postprocess=setenv,
        help="list of X=Y lines with environment variable settings",
    )

    def basepython_default(testenv_config, value):
        """either user set or proposed from the factor name

        in both cases we check that the factor name implied python version and the resolved
        python interpreter version match up; if they don't we warn, unless ignore base
        python conflict is set in which case the factor name implied version if forced
        """
        for factor in testenv_config.factors:
            match = tox.PYTHON.PY_FACTORS_RE.match(factor)
            if match:
                base_exe = {"py": "python"}.get(match.group(1), match.group(1))
                version_s = match.group(2)
                if not version_s:
                    version_info = ()
                elif len(version_s) == 1:
                    version_info = (version_s,)
                else:
                    version_info = (version_s[0], version_s[1:])
                implied_version = ".".join(version_info)
                implied_python = "{}{}".format(base_exe, implied_version)
                break
        else:
            implied_python, version_info, implied_version = None, (), ""

        if testenv_config.config.ignore_basepython_conflict and implied_python is not None:
            return implied_python

        proposed_python = (implied_python or sys.executable) if value is None else str(value)
        if implied_python is not None and implied_python != proposed_python:
            testenv_config.basepython = proposed_python
            python_info_for_proposed = testenv_config.python_info
            if not isinstance(python_info_for_proposed, NoInterpreterInfo):
                proposed_version = ".".join(
                    str(x) for x in python_info_for_proposed.version_info[: len(version_info)]
                )
                if proposed_version != implied_version:
                    # TODO(stephenfin): Raise an exception here in tox 4.0
                    warnings.warn(
                        "conflicting basepython version (set {}, should be {}) for env '{}';"
                        "resolve conflict or set ignore_basepython_conflict".format(
                            proposed_version, implied_version, testenv_config.envname
                        )
                    )

        return proposed_python

    parser.add_testenv_attribute(
        name="basepython",
        type="basepython",
        default=None,
        postprocess=basepython_default,
        help="executable name or path of interpreter used to create a virtual test environment.",
    )

    def merge_description(testenv_config, value):
        """the reader by default joins generated description with new line,
         replace new line with space"""
        return value.replace("\n", " ")

    parser.add_testenv_attribute(
        name="description",
        type="string",
        default="",
        postprocess=merge_description,
        help="short description of this environment",
    )

    parser.add_testenv_attribute(
        name="envtmpdir", type="path", default="{envdir}/tmp", help="venv temporary directory"
    )

    parser.add_testenv_attribute(
        name="envlogdir", type="path", default="{envdir}/log", help="venv log directory"
    )

    parser.add_testenv_attribute(
        name="downloadcache",
        type="string",
        default=None,
        help="(ignored) has no effect anymore, pip-8 uses local caching by default",
    )

    parser.add_testenv_attribute(
        name="changedir",
        type="path",
        default="{toxinidir}",
        help="directory to change to when running commands",
    )

    parser.add_testenv_attribute_obj(PosargsOption())

    parser.add_testenv_attribute(
        name="skip_install",
        type="bool",
        default=False,
        help="Do not install the current package. This can be used when you need the virtualenv "
        "management but do not want to install the current package",
    )

    parser.add_testenv_attribute(
        name="ignore_errors",
        type="bool",
        default=False,
        help="if set to True all commands will be executed irrespective of their result error "
        "status.",
    )

    def recreate(testenv_config, value):
        if testenv_config.config.option.recreate:
            return True
        return value

    parser.add_testenv_attribute(
        name="recreate",
        type="bool",
        default=False,
        postprocess=recreate,
        help="always recreate this test environment.",
    )

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
            str(PARALLEL_ENV_VAR_KEY),
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

    parser.add_testenv_attribute(
        name="passenv",
        type="line-list",
        postprocess=passenv,
        help="environment variables needed during executing test commands (taken from invocation "
        "environment). Note that tox always  passes through some basic environment variables "
        "which are needed for basic functioning of the Python system. See --showconfig for the "
        "eventual passenv setting.",
    )

    parser.add_testenv_attribute(
        name="whitelist_externals",
        type="line-list",
        help="each lines specifies a path or basename for which tox will not warn "
        "about it coming from outside the test environment.",
    )

    parser.add_testenv_attribute(
        name="platform",
        type="string",
        default=".*",
        help="regular expression which must match against ``sys.platform``. "
        "otherwise testenv will be skipped.",
    )

    def sitepackages(testenv_config, value):
        return testenv_config.config.option.sitepackages or value

    def alwayscopy(testenv_config, value):
        return testenv_config.config.option.alwayscopy or value

    parser.add_testenv_attribute(
        name="sitepackages",
        type="bool",
        default=False,
        postprocess=sitepackages,
        help="Set to ``True`` if you want to create virtual environments that also "
        "have access to globally installed packages.",
    )

    parser.add_testenv_attribute(
        "download",
        type="bool",
        default=False,
        help="download the latest pip, setuptools and wheel when creating the virtual"
        "environment (default is to use the one bundled in virtualenv)",
    )

    parser.add_testenv_attribute(
        name="alwayscopy",
        type="bool",
        default=False,
        postprocess=alwayscopy,
        help="Set to ``True`` if you want virtualenv to always copy files rather "
        "than symlinking.",
    )

    def pip_pre(testenv_config, value):
        return testenv_config.config.option.pre or value

    parser.add_testenv_attribute(
        name="pip_pre",
        type="bool",
        default=False,
        postprocess=pip_pre,
        help="If ``True``, adds ``--pre`` to the ``opts`` passed to the install command. ",
    )

    def develop(testenv_config, value):
        option = testenv_config.config.option
        return not option.installpkg and (value or option.develop or option.devenv is not None)

    parser.add_testenv_attribute(
        name="usedevelop",
        type="bool",
        postprocess=develop,
        default=False,
        help="install package in develop/editable mode",
    )

    parser.add_testenv_attribute_obj(InstallcmdOption())

    parser.add_testenv_attribute(
        name="list_dependencies_command",
        type="argv",
        default="python -m pip freeze",
        help="list dependencies for a virtual environment",
    )

    parser.add_testenv_attribute_obj(DepOption())

    parser.add_testenv_attribute(
        name="commands",
        type="argvlist",
        default="",
        help="each line specifies a test command and can use substitution.",
    )

    parser.add_testenv_attribute(
        name="commands_pre",
        type="argvlist",
        default="",
        help="each line specifies a setup command action and can use substitution.",
    )

    parser.add_testenv_attribute(
        name="commands_post",
        type="argvlist",
        default="",
        help="each line specifies a teardown command and can use substitution.",
    )

    parser.add_testenv_attribute(
        "ignore_outcome",
        type="bool",
        default=False,
        help="if set to True a failing result of this testenv will not make "
        "tox fail, only a warning will be produced",
    )

    parser.add_testenv_attribute(
        "extras",
        type="line-list",
        help="list of extras to install with the source distribution or develop install",
    )

    add_parallel_config(parser)