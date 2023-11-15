    def _violation(self, operation, *args, **kw):
        from pex.third_party.setuptools.sandbox import SandboxViolation
        raise SandboxViolation(operation, args, kw)