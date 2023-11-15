    def dump(type, exc):
        """
        Always return a dumped (pickled) type and exc. If exc can't be pickled,
        wrap it in UnpickleableException first.
        """
        try:
            return pickle.dumps(type), pickle.dumps(exc)
        except Exception:
            # get UnpickleableException inside the sandbox
            from pex.third_party.setuptools.sandbox import UnpickleableException as cls
            return cls.dump(cls, cls(repr(exc)))