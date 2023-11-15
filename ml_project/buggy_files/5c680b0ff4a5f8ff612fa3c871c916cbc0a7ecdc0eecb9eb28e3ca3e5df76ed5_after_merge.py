    def parse(self, s, filename='<code>', mode='exec', debug_level=0):
        """Returns an abstract syntax tree of xonsh code.

        Parameters
        ----------
        s : str
            The xonsh code.
        filename : str, optional
            Name of the file.
        mode : str, optional
            Execution mode, one of: exec, eval, or single.
        debug_level : str, optional
            Debugging level passed down to yacc.

        Returns
        -------
        tree : AST
        """
        self.reset()
        self.xonsh_code = s
        self.lexer.fname = filename
        while self.parser is None:
            time.sleep(0.01)  # block until the parser is ready
        tree = self.parser.parse(input=s, lexer=self.lexer, debug=debug_level)
        if tree is not None:
            check_contexts(tree)
        # hack for getting modes right
        if mode == 'single':
            if isinstance(tree, ast.Expression):
                tree = ast.Interactive(body=[self.expr(tree.body)])
            elif isinstance(tree, ast.Module):
                tree = ast.Interactive(body=tree.body)
        return tree