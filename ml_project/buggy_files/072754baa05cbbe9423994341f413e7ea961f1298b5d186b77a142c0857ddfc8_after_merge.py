    def lower(self):
        # Emit the Env into the module
        self.emit_environment_object()
        if self.generator_info is None:
            self.genlower = None
            self.lower_normal_function(self.fndesc)
        else:
            self.genlower = self.GeneratorLower(self)
            self.gentype = self.genlower.gentype

            self.genlower.lower_init_func(self)
            self.genlower.lower_next_func(self)
            if self.gentype.has_finalizer:
                self.genlower.lower_finalize_func(self)

        if config.DUMP_LLVM:
            print(("LLVM DUMP %s" % self.fndesc).center(80, '-'))
            if config.HIGHLIGHT_DUMPS:
                try:
                    from pygments import highlight
                    from pygments.lexers import LlvmLexer as lexer
                    from pygments.formatters import Terminal256Formatter
                    print(highlight(self.module.__repr__(), lexer(),
                                    Terminal256Formatter(
                                        style='solarized-light')))
                except ImportError:
                    msg = "Please install pygments to see highlighted dumps"
                    raise ValueError(msg)
            else:
                print(self.module)
            print('=' * 80)

        # Special optimization to remove NRT on functions that do not need it.
        if self.context.enable_nrt and self.generator_info is None:
            removerefctpass.remove_unnecessary_nrt_usage(self.function,
                                                         context=self.context,
                                                         fndesc=self.fndesc)

        # Run target specific post lowering transformation
        self.context.post_lowering(self.module, self.library)

        # Materialize LLVM Module
        self.library.add_ir_module(self.module)