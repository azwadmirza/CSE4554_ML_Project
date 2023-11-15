    def runsource(self, source, filename='<input>', symbol='single'):
        global SIMPLE_TRACEBACKS
        try:
            tokens = tokenize(source)
        except PrematureEndOfInput:
            return True
        except LexException as e:
            if e.source is None:
                e.source = source
                e.filename = filename
            sys.stderr.write(str(e))
            return False

        try:
            _ast = hy_compile(tokens, "__console__", root=ast.Interactive)
            if self.spy:
                print_python_code(_ast)
            code = ast_compile(_ast, filename, symbol)
        except HyTypeError as e:
            if e.source is None:
                e.source = source
                e.filename = filename
            if SIMPLE_TRACEBACKS:
                sys.stderr.write(str(e))
            else:
                self.showtraceback()
            return False
        except Exception:
            self.showtraceback()
            return False

        self.runcode(code)
        return False