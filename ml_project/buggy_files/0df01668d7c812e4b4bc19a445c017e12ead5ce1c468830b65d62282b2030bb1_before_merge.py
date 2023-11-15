    def __init__(self, config, inipath):
        config.toxinipath = inipath
        config.toxinidir = config.toxinipath.dirpath()

        self._cfg = py.iniconfig.IniConfig(config.toxinipath)
        config._cfg = self._cfg
        self.config = config

        if inipath.basename == 'setup.cfg':
            prefix = 'tox'
        else:
            prefix = None
        ctxname = getcontextname()
        if ctxname == "jenkins":
            reader = SectionReader("tox:jenkins", self._cfg, prefix=prefix,
                                   fallbacksections=['tox'])
            distshare_default = "{toxworkdir}/distshare"
        elif not ctxname:
            reader = SectionReader("tox", self._cfg, prefix=prefix)
            distshare_default = "{homedir}/.tox/distshare"
        else:
            raise ValueError("invalid context")

        if config.option.hashseed is None:
            hashseed = make_hashseed()
        elif config.option.hashseed == 'noset':
            hashseed = None
        else:
            hashseed = config.option.hashseed
        config.hashseed = hashseed

        reader.addsubstitutions(toxinidir=config.toxinidir,
                                homedir=config.homedir)
        # As older versions of tox may have bugs or incompatabilities that
        # prevent parsing of tox.ini this must be the first thing checked.
        config.minversion = reader.getstring("minversion", None)
        if config.minversion:
            minversion = NormalizedVersion(self.config.minversion)
            toxversion = NormalizedVersion(tox.__version__)
            if toxversion < minversion:
                raise tox.exception.MinVersionError(
                    "tox version is %s, required is at least %s" % (
                        toxversion, minversion))
        if config.option.workdir is None:
            config.toxworkdir = reader.getpath("toxworkdir", "{toxinidir}/.tox")
        else:
            config.toxworkdir = config.toxinidir.join(config.option.workdir, abs=True)

        if not config.option.skip_missing_interpreters:
            config.option.skip_missing_interpreters = \
                reader.getbool("skip_missing_interpreters", False)

        # determine indexserver dictionary
        config.indexserver = {'default': IndexServerConfig('default')}
        prefix = "indexserver"
        for line in reader.getlist(prefix):
            name, url = map(lambda x: x.strip(), line.split("=", 1))
            config.indexserver[name] = IndexServerConfig(name, url)

        override = False
        if config.option.indexurl:
            for urldef in config.option.indexurl:
                m = re.match(r"\W*(\w+)=(\S+)", urldef)
                if m is None:
                    url = urldef
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

        reader.addsubstitutions(toxworkdir=config.toxworkdir)
        config.distdir = reader.getpath("distdir", "{toxworkdir}/dist")
        reader.addsubstitutions(distdir=config.distdir)
        config.distshare = reader.getpath("distshare", distshare_default)
        reader.addsubstitutions(distshare=config.distshare)
        config.sdistsrc = reader.getpath("sdistsrc", None)
        config.setupdir = reader.getpath("setupdir", "{toxinidir}")
        config.logdir = config.toxworkdir.join("log")

        config.envlist, all_envs = self._getenvdata(reader)

        # factors used in config or predefined
        known_factors = self._list_section_factors("testenv")
        known_factors.update(default_factors)
        known_factors.add("python")

        # factors stated in config envlist
        stated_envlist = reader.getstring("envlist", replace=False)
        if stated_envlist:
            for env in _split_env(stated_envlist):
                known_factors.update(env.split('-'))

        # configure testenvs
        for name in all_envs:
            section = testenvprefix + name
            factors = set(name.split('-'))
            if section in self._cfg or factors <= known_factors:
                config.envconfigs[name] = \
                    self.make_envconfig(name, section, reader._subs, config,
                                        replace=name in config.envlist)

        all_develop = all(name in config.envconfigs
                          and config.envconfigs[name].usedevelop
                          for name in config.envlist)

        config.skipsdist = reader.getbool("skipsdist", all_develop)