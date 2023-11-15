    def from_fndesc(cls, fndesc):
        mod = fndesc.lookup_module()
        try:
            # Avoid creating new Env
            return cls._memo[fndesc.env_name]
        except KeyError:
            inst = cls(mod.__dict__)
            inst.env_name = fndesc.env_name
            cls._memo[fndesc.env_name] = inst
            return inst