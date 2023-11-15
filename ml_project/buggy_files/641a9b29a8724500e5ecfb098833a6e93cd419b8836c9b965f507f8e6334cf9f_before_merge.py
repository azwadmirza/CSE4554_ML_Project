    def make_envconfig(self, name, section, subs, config, replace=True):
        factors = set(name.split('-'))
        reader = SectionReader(section, self._cfg, fallbacksections=["testenv"],
                               factors=factors)
        vc = TestenvConfig(config=config, envname=name, factors=factors, reader=reader)
        reader.addsubstitutions(**subs)
        reader.addsubstitutions(envname=name)
        reader.addsubstitutions(envbindir=vc.get_envbindir,
                                envsitepackagesdir=vc.get_envsitepackagesdir,
                                envpython=vc.get_envpython)

        for env_attr in config._testenv_attr:
            atype = env_attr.type
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
                res = env_attr.postprocess(testenv_config=vc, value=res)
            setattr(vc, env_attr.name, res)

            if atype in ("path", "string"):
                reader.addsubstitutions(**{env_attr.name: res})

        return vc