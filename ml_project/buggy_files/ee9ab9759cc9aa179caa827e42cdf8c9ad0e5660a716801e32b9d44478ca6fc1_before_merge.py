    def __init__(self, **kwds):
        self._version = None
        self._default_variable_value = None

        self._capabilities = Options()
        self._capabilities.linear = True
        self._capabilities.quadratic_objective = True
        self._capabilities.quadratic_constraint = True
        self._capabilities.integer = True
        self._capabilities.sos1 = False
        self._capabilities.sos2 = False

        self.options = Options() # ignored

        pyomo.common.plugin.Plugin.__init__(self, **kwds)