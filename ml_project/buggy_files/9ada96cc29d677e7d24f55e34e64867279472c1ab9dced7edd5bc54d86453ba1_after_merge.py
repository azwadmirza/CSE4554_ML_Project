    def __call__(self, source, filename="<input>", symbol="single"):
        try:
            hy_ast = hy_parse(source, filename=filename)
            root_ast = ast.Interactive if symbol == 'single' else ast.Module

            # Our compiler doesn't correspond to a real, fixed source file, so
            # we need to [re]set these.
            self.hy_compiler.filename = filename
            self.hy_compiler.source = source
            exec_ast, eval_ast = hy_compile(hy_ast, self.module, root=root_ast,
                                            get_expr=True,
                                            compiler=self.hy_compiler,
                                            filename=filename, source=source)

            if self.ast_callback:
                self.ast_callback(exec_ast, eval_ast)

            exec_code = ast_compile(exec_ast, filename, symbol)
            eval_code = ast_compile(eval_ast, filename, 'eval')

            return exec_code, eval_code
        except PrematureEndOfInput:
            # Save these so that we can reraise/display when an incomplete
            # interactive command is given at the prompt.
            sys.last_type, sys.last_value, sys.last_traceback = sys.exc_info()
            return None