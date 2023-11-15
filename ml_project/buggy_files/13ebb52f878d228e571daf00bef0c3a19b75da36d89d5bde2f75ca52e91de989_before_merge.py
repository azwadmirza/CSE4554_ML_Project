    def __init__(self, options, interpreter):
        super(Venv, self).__init__(options, interpreter)
        self.can_be_inline = interpreter is CURRENT and interpreter.executable == interpreter.system_executable
        self._context = None
        self.builtin_way = options.builtin_way