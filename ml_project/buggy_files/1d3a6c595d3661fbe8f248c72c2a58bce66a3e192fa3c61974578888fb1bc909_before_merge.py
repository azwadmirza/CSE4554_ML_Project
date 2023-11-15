    def handle_signature(self, sig, signode):
        if 'cpp:parentSymbol' not in self.env.ref_context:
            root = self.env.domaindata['cpp']['rootSymbol']
            self.env.ref_context['cpp:parentSymbol'] = root
        parentSymbol = self.env.ref_context['cpp:parentSymbol']

        parser = DefinitionParser(sig, self)
        try:
            ast = self.parse_definition(parser)
            parser.assert_end()
        except DefinitionError as e:
            self.warn(e.description)
            # It is easier to assume some phony name than handling the error in
            # the possibly inner declarations.
            name = _make_phony_error_name()
            symbol = parentSymbol.add_name(name)
            self.env.ref_context['cpp:lastSymbol'] = symbol
            raise ValueError
        symbol = parentSymbol.add_declaration(ast, docname=self.env.docname)
        self.env.ref_context['cpp:lastSymbol'] = symbol

        if ast.objectType == 'enumerator':
            self._add_enumerator_to_parent(ast)

        self.describe_signature(signode, ast)
        return ast