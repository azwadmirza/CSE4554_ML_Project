    def __init__(self, config, ini_path, ini_data):  # noqa
        config.toxinipath = ini_path
        using("tox.ini: {} (pid {})".format(config.toxinipath, os.getpid()))
        config.toxinidir = config.toxinipath.dirpath()

        self._cfg = py.iniconfig.IniConfig(config.toxinipath, ini_data)
        previous_line_of = self._cfg.lineof

        def line_of_default_to_zero(section, name=None):
            at = previous_line_of(section, name=name)
            if at is None:
                at = 0
            return at

        self._cfg.lineof = line_of_default_to_zero
        config._cfg = self._cfg
        self.config = config

        prefix = "tox" if ini_path.basename == "setup.cfg" else None

        context_name = getcontextname()
        if context_name == "jenkins":
            reader = SectionReader(
                "tox:jenkins", self._cfg, prefix=prefix, fallbacksections=["tox"]
            )
            dist_share_default = "{toxworkdir}/distshare"
        elif not context_name:
            reader = SectionReader("tox", self._cfg, prefix=prefix)
            dist_share_default = "{homedir}/.tox/distshare"
        else:
            raise ValueError("invalid context")

        if config.option.hashseed is None:
            hash_seed = make_hashseed()
        elif config.option.hashseed == "noset":
            hash_seed = None
        else:
            hash_seed = config.option.hashseed
        config.hashseed = hash_seed

        reader.addsubstitutions(toxinidir=config.toxinidir, homedir=config.homedir)

        if config.option.workdir is None:
            config.toxworkdir = reader.getpath("toxworkdir", "{toxinidir}/.tox")
        else:
            config.toxworkdir = config.toxinidir.join(config.option.workdir, abs=True)

        if os.path.exists(str(config.toxworkdir)):
            config.toxworkdir = config.toxworkdir.realpath()

        reader.addsubstitutions(toxworkdir=config.toxworkdir)
        config.ignore_basepython_conflict = reader.getbool("ignore_basepython_conflict", False)

        config.distdir = reader.getpath("distdir", "{toxworkdir}/dist")

        reader.addsubstitutions(distdir=config.distdir)
        config.distshare = reader.getpath("distshare", dist_share_default)
        config.temp_dir = reader.getpath("temp_dir", "{toxworkdir}/.tmp")
        reader.addsubstitutions(distshare=config.distshare)
        config.sdistsrc = reader.getpath("sdistsrc", None)
        config.setupdir = reader.getpath("setupdir", "{toxinidir}")
        config.logdir = config.toxworkdir.join("log")
        within_parallel = PARALLEL_ENV_VAR_KEY in os.environ
        if not within_parallel and not WITHIN_PROVISION:
            ensure_empty_dir(config.logdir)

        # determine indexserver dictionary
        config.indexserver = {"default": IndexServerConfig("default")}
        prefix = "indexserver"
        for line in reader.getlist(prefix):
            name, url = map(lambda x: x.strip(), line.split("=", 1))
            config.indexserver[name] = IndexServerConfig(name, url)

        if config.option.skip_missing_interpreters == "config":
            val = reader.getbool("skip_missing_interpreters", False)
            config.option.skip_missing_interpreters = "true" if val else "false"

        override = False
        if config.option.indexurl:
            for url_def in config.option.indexurl:
                m = re.match(r"\W*(\w+)=(\S+)", url_def)
                if m is None:
                    url = url_def
                    name = "default"
                else:
                    name, url = m.groups()
                    if not url:
                        url = None
                if name != "ALL":
                    config.indexserver[name].url = url
                else:
                    override = url
        # let ALL override all existing entries
        if override:
            for name in config.indexserver:
                config.indexserver[name] = IndexServerConfig(name, override)

        self.handle_provision(config, reader)

        self.parse_build_isolation(config, reader)
        res = self._getenvdata(reader, config)
        config.envlist, all_envs, config.envlist_default, config.envlist_explicit = res

        # factors used in config or predefined
        known_factors = self._list_section_factors("testenv")
        known_factors.update({"py", "python"})

        # factors stated in config envlist
        stated_envlist = reader.getstring("envlist", replace=False)
        if stated_envlist:
            for env in _split_env(stated_envlist):
                known_factors.update(env.split("-"))

        # configure testenvs
        to_do = []
        failures = OrderedDict()
        results = {}
        cur_self = self

        def run(name, section, subs, config):
            try:
                results[name] = cur_self.make_envconfig(name, section, subs, config)
            except Exception as exception:
                failures[name] = (exception, traceback.format_exc())

        order = []
        for name in all_envs:
            section = "{}{}".format(testenvprefix, name)
            factors = set(name.split("-"))
            if (
                section in self._cfg
                or factors <= known_factors
                or all(
                    tox.PYTHON.PY_FACTORS_RE.match(factor) for factor in factors - known_factors
                )
            ):
                order.append(name)
                thread = Thread(target=run, args=(name, section, reader._subs, config))
                thread.daemon = True
                thread.start()
                to_do.append(thread)
        for thread in to_do:
            while thread.is_alive():
                thread.join(timeout=20)
        if failures:
            raise tox.exception.ConfigError(
                "\n".join(
                    "{} failed with {} at {}".format(key, exc, trace)
                    for key, (exc, trace) in failures.items()
                )
            )
        for name in order:
            config.envconfigs[name] = results[name]
        all_develop = all(
            name in config.envconfigs and config.envconfigs[name].usedevelop
            for name in config.envlist
        )

        config.skipsdist = reader.getbool("skipsdist", all_develop)

        if config.option.devenv is not None:
            config.option.notest = True

        if config.option.devenv is not None and len(config.envlist) != 1:
            feedback("--devenv requires only a single -e", sysexit=True)