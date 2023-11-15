    def __init__(self, envname, config, factors, reader):
        #: test environment name
        self.envname = envname
        #: global tox config object
        self.config = config
        #: set of factors
        self.factors = factors
        self._reader = reader
        self.missing_subs = []
        """Holds substitutions that could not be resolved.

        Pre 2.8.1 missing substitutions crashed with a ConfigError although this would not be a
        problem if the env is not part of the current testrun. So we need to remember this and
        check later when the testenv is actually run and crash only then.
        """