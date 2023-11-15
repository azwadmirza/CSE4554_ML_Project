    def make_envconfig(self, name, section, subs, config, replace=True):
        factors = set(name.split('-'))
        reader = SectionReader(section, self._cfg, fallbacksections=["testenv"],
                               factors=factors)
        tc = TestenvConfig(name, config, factors, reader)
        reader.addsubstitutions(
            envname=name, envbindir=tc.get_envbindir, envsitepackagesdir=tc.get_envsitepackagesdir,
            envpython=tc.get_envpython, **subs)
        for env_attr in config._testenv_attr:
            atype = env_attr.type
            try:
                if atype in ("bool", "path", "string", "dict", "dict_setenv", "argv", "argvlist"):
                    meth = getattr(reader, "get" + atype)
                    res = meth(env_attr.name, env_attr.default, replace=replace)
                elif atype == "space-separated-list":
                    res = reader.getlist(env_attr.name, sep=" ")
                elif atype == "line-list":
                    res = reader.getlist(env_attr.name, sep="\n")
                else:
                    raise ValueError("unknown type %r" % (atype,))
                if env_attr.postprocess:
                    res = env_attr.postprocess(testenv_config=tc, value=res)
            except tox.exception.MissingSubstitution as e:
                tc.missing_subs.append(e.name)
                res = e.FLAG
            setattr(tc, env_attr.name, res)
            if atype in ("path", "string"):
                reader.addsubstitutions(**{env_attr.name: res})
        return tc