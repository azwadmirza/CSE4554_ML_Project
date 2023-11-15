    def __init__(self, *regs, name=None):
        if any([not isinstance(reg, (QuantumRegister, ClassicalRegister)) for reg in regs]):
            try:
                regs = tuple(int(reg) for reg in regs)
            except Exception:
                raise CircuitError("Circuit args must be Registers or be castable to an int" +
                                   "(%s '%s' was provided)"
                                   % ([type(reg).__name__ for reg in regs], regs))
        if name is None:
            name = self.cls_prefix() + str(self.cls_instances())
            if sys.platform != "win32" and not is_main_process():
                name += '-{}'.format(mp.current_process().pid)
        self._increment_instances()

        if not isinstance(name, str):
            raise CircuitError("The circuit name should be a string "
                               "(or None to auto-generate a name).")

        self.name = name

        # Data contains a list of instructions and their contexts,
        # in the order they were applied.
        self._data = []

        # This is a map of registers bound to this circuit, by name.
        self.qregs = []
        self.cregs = []
        self.add_register(*regs)

        # Parameter table tracks instructions with variable parameters.
        self._parameter_table = ParameterTable()

        self._layout = None