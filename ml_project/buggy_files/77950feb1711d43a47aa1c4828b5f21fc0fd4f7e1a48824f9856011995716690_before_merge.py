    def handle_signature(self, sig, signode):
        parser = DefinitionParser(sig)
        try:
            ast = self.parse_definition(parser)
            parser.assert_end()
        except DefinitionError as e:
            self.state_machine.reporter.warning(e.description,
                                                line=self.lineno)
            raise ValueError
        self.describe_signature(signode, ast)

        parent = self.env.ref_context.get('cpp:parent')
        if parent and len(parent) > 0:
            ast = ast.clone()
            ast.prefixedName = ast.name.prefix_nested_name(parent[-1])
        else:
            ast.prefixedName = ast.name
        return ast