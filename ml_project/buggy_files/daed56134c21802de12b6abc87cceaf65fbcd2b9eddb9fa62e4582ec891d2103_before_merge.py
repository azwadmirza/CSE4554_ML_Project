    def runsource(self, source, filename='<input>', symbol='single'):

        try:
            do = hy_parse(source, filename=filename)
        except PrematureEndOfInput:
            return True
        except HySyntaxError as e:
            self.showsyntaxerror(filename=filename)
            return False

        try:
            # Our compiler doesn't correspond to a real, fixed source file, so
            # we need to [re]set these.
            self.hy_compiler.filename = filename
            self.hy_compiler.source = source
            value = hy_eval(do, self.locals, self.module, self.ast_callback,
                            compiler=self.hy_compiler, filename=filename,
                            source=source)
        except SystemExit:
            raise
        except Exception as e:
            self.showtraceback()
            return False

        if value is not None:
            # Shift exisitng REPL results
            next_result = value
            for sym in self._repl_results_symbols:
                self.locals[sym], next_result = next_result, self.locals[sym]

            # Print the value.
            try:
                output = self.output_fn(value)
            except Exception:
                self.showtraceback()
                return False

            print(output)

        return False