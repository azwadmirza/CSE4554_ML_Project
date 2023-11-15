    def ast_callback(self, exec_ast, eval_ast):
        if self.spy:
            try:
                # Mush the two AST chunks into a single module for
                # conversion into Python.
                new_ast = ast.Module(exec_ast.body +
                                     [ast.Expr(eval_ast.body)])
                print(astor.to_source(new_ast))
            except Exception:
                msg = 'Exception in AST callback:\n{}\n'.format(
                    traceback.format_exc())
                self.write(msg)