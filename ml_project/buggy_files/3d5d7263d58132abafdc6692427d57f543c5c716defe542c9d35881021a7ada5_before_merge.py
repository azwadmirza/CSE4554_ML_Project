    def ast_callback(self, main_ast, expr_ast):
        if self.spy:
            # Mush the two AST chunks into a single module for
            # conversion into Python.
            new_ast = ast.Module(main_ast.body +
                                 [ast.Expr(expr_ast.body)])
            print(astor.to_source(new_ast))