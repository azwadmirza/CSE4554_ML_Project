    def _violation(self, operation, *args, **kw):
        if "__PEX_UNVENDORED__" in __import__("os").environ:
          from setuptools.sandbox import SandboxViolation  # vendor:skip
        else:
          from pex.third_party.setuptools.sandbox import SandboxViolation

        raise SandboxViolation(operation, args, kw)