    def runsource(self, source, filename='<stdin>', symbol='exec'):
        try:
            res = super(HyREPL, self).runsource(source, filename, symbol)
        except (HyMacroExpansionError, HyRequireError):
            # We need to handle these exceptions ourselves, because the base
            # method only handles `OverflowError`, `SyntaxError` and
            # `ValueError`.
            self.showsyntaxerror(filename)
            return False
        except (HyLanguageError):
            # Our compiler will also raise `TypeError`s
            self.showtraceback()
            return False

        # Shift exisitng REPL results
        if not res:
            next_result = self.last_value
            for sym in self._repl_results_symbols:
                self.locals[sym], next_result = next_result, self.locals[sym]

            # Print the value.
            if self.print_last_value:
                try:
                    output = self.output_fn(self.last_value)
                except Exception:
                    self.showtraceback()
                    return False

                print(output)

        return res