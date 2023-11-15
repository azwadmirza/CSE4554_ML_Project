    def from_fndesc(cls, fndesc):
        try:
            # Avoid creating new Env
            return cls._memo[fndesc.env_name]
        except KeyError:
            inst = cls(fndesc.lookup_globals())
            inst.env_name = fndesc.env_name
            cls._memo[fndesc.env_name] = inst
            return inst