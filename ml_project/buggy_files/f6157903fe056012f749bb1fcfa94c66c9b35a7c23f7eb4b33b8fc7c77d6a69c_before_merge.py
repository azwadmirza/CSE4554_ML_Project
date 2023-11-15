    def make_envconfig(self, name, section, subs, config, replace=True):
        factors = set(name.split("-"))
        reader = SectionReader(section, self._cfg, fallbacksections=["testenv"], factors=factors)
        tc = TestenvConfig(name, config, factors, reader)
        reader.addsubstitutions(
            envname=name,
            envbindir=tc.get_envbindir,
            envsitepackagesdir=tc.get_envsitepackagesdir,
            envpython=tc.get_envpython,
            **subs
        )
        for env_attr in config._testenv_attr:
            atype = env_attr.type
            try:
                if atype in (
                    "bool",
                    "float",
                    "path",
                    "string",
                    "dict",
                    "dict_setenv",
                    "argv",
                    "argvlist",
                    "argv_install_command",
                ):
                    meth = getattr(reader, "get{}".format(atype))
                    res = meth(env_attr.name, env_attr.default, replace=replace)
                elif atype == "basepython":
                    no_fallback = name in (config.provision_tox_env,)
                    res = reader.getstring(
                        env_attr.name,
                        env_attr.default,
                        replace=replace,
                        no_fallback=no_fallback,
                    )
                elif atype == "space-separated-list":
                    res = reader.getlist(env_attr.name, sep=" ")
                elif atype == "line-list":
                    res = reader.getlist(env_attr.name, sep="\n")
                elif atype == "env-list":
                    res = reader.getstring(env_attr.name, replace=False)
                    res = tuple(_split_env(res))
                else:
                    raise ValueError("unknown type {!r}".format(atype))
                if env_attr.postprocess:
                    res = env_attr.postprocess(testenv_config=tc, value=res)
            except tox.exception.MissingSubstitution as e:
                tc._missing_subs.append(e.name)
                res = e.FLAG
            setattr(tc, env_attr.name, res)
            if atype in ("path", "string", "basepython"):
                reader.addsubstitutions(**{env_attr.name: res})
        return tc