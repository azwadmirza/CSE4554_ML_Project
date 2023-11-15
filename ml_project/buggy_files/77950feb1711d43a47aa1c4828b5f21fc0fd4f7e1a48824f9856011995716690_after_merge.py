    def handle_signature(self, sig, signode):
        def set_lastname(name):
            parent = self.env.ref_context.get('cpp:parent')
            if parent and len(parent) > 0:
                res = name.prefix_nested_name(parent[-1])
            else:
                res = name
            assert res
            self.env.ref_context['cpp:lastname'] = res
            return res

        parser = DefinitionParser(sig)
        try:
            ast = self.parse_definition(parser)
            parser.assert_end()
        except DefinitionError as e:
            self.state_machine.reporter.warning(e.description,
                                                line=self.lineno)
            # It is easier to assume some phony name than handling the error in
            # the possibly inner declarations.
            name = ASTNestedName([
                ASTNestedNameElement("PhonyNameDueToError", None)
            ])
            set_lastname(name)
            raise ValueError
        self.describe_signature(signode, ast)

        ast.prefixedName = set_lastname(ast.name)
        assert ast.prefixedName
        return ast