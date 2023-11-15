    def dump(type, exc):
        """
        Always return a dumped (pickled) type and exc. If exc can't be pickled,
        wrap it in UnpickleableException first.
        """
        try:
            return pickle.dumps(type), pickle.dumps(exc)
        except Exception:
            # get UnpickleableException inside the sandbox
            if "__PEX_UNVENDORED__" in __import__("os").environ:
              from setuptools.sandbox import UnpickleableException as cls  # vendor:skip
            else:
              from pex.third_party.setuptools.sandbox import UnpickleableException as cls

            return cls.dump(cls, cls(repr(exc)))