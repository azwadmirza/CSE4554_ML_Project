    def __init__(self, spy=False, output_fn=None, locals=None,
                 filename="<stdin>"):

        # Create a proper module for this REPL so that we can obtain it easily
        # (e.g. using `importlib.import_module`).
        # We let `InteractiveConsole` initialize `self.locals` when it's
        # `None`.
        super(HyREPL, self).__init__(locals=locals,
                                     filename=filename)

        module_name = self.locals.get('__name__', '__console__')
        # Make sure our newly created module is properly introduced to
        # `sys.modules`, and consistently use its namespace as `self.locals`
        # from here on.
        self.module = sys.modules.setdefault(module_name,
                                             types.ModuleType(module_name))
        self.module.__dict__.update(self.locals)
        self.locals = self.module.__dict__

        # Load cmdline-specific macros.
        require('hy.cmdline', self.module, assignments='ALL')

        self.hy_compiler = HyASTCompiler(self.module)

        self.compile = HyCommandCompiler(self.module, self.ast_callback,
                                         self.hy_compiler)

        self.spy = spy
        self.last_value = None

        if output_fn is None:
            self.output_fn = repr
        elif callable(output_fn):
            self.output_fn = output_fn
        else:
            if "." in output_fn:
                parts = [mangle(x) for x in output_fn.split(".")]
                module, f = '.'.join(parts[:-1]), parts[-1]
                self.output_fn = getattr(importlib.import_module(module), f)
            else:
                self.output_fn = __builtins__[mangle(output_fn)]

        # Pre-mangle symbols for repl recent results: *1, *2, *3
        self._repl_results_symbols = [mangle("*{}".format(i + 1)) for i in range(3)]
        self.locals.update({sym: None for sym in self._repl_results_symbols})