    def _add_symbols(self, nestedName, templateDecls, declaration, docname):
        # This condition should be checked at the parser level.
        # Each template argument list must have a template parameter list.
        # But to declare a template there must be an additional template parameter list.
        assert(nestedName.num_templates() == len(templateDecls) or
               nestedName.num_templates() + 1 == len(templateDecls))

        parentSymbol = self
        if nestedName.rooted:
            while parentSymbol.parent:
                parentSymbol = parentSymbol.parent
        names = nestedName.names
        iTemplateDecl = 0
        for name in names[:-1]:
            # there shouldn't be anything inside an operator
            # (other than template parameters, which are not added this way, right?)
            assert not name.is_operator()
            identifier = name.identifier
            templateArgs = name.templateArgs
            if templateArgs:
                assert iTemplateDecl < len(templateDecls)
                templateParams = templateDecls[iTemplateDecl]
                iTemplateDecl += 1
            else:
                templateParams = None
            symbol = parentSymbol._find_named_symbol(identifier,
                                                     templateParams,
                                                     templateArgs,
                                                     operator=None,
                                                     templateShorthand=False,
                                                     matchSelf=False)
            if symbol is None:
                symbol = Symbol(parent=parentSymbol, identifier=identifier,
                                templateParams=templateParams,
                                templateArgs=templateArgs, declaration=None,
                                docname=None)
            parentSymbol = symbol
        name = names[-1]
        if name.is_operator():
            identifier = None
            templateArgs = None
            operator = name
        else:
            identifier = name.identifier
            templateArgs = name.templateArgs
            operator = None
        if iTemplateDecl < len(templateDecls):
            if iTemplateDecl + 1 != len(templateDecls):
                print(text_type(templateDecls))
                print(text_type(nestedName))
            assert iTemplateDecl + 1 == len(templateDecls)
            templateParams = templateDecls[iTemplateDecl]
        else:
            assert iTemplateDecl == len(templateDecls)
            templateParams = None
        symbol = parentSymbol._find_named_symbol(identifier,
                                                 templateParams,
                                                 templateArgs,
                                                 operator,
                                                 templateShorthand=False,
                                                 matchSelf=False)
        if symbol:
            if not declaration:
                # good, just a scope creation
                return symbol
            if not symbol.declaration:
                # If someone first opened the scope, and then later
                # declares it, e.g,
                # .. namespace:: Test
                # .. namespace:: nullptr
                # .. class:: Test
                symbol._fill_empty(declaration, docname)
                return symbol
            # It may simply be a functin overload, so let's compare ids.
            candSymbol = Symbol(parent=parentSymbol, identifier=identifier,
                                templateParams=templateParams,
                                templateArgs=templateArgs,
                                declaration=declaration,
                                docname=docname)
            newId = declaration.get_newest_id()
            oldId = symbol.declaration.get_newest_id()
            if newId != oldId:
                # we already inserted the symbol, so return the new one
                symbol = candSymbol
            else:
                # Redeclaration of the same symbol.
                # Let the new one be there, but raise an error to the client
                # so it can use the real symbol as subscope.
                # This will probably result in a duplicate id warning.
                raise _DuplicateSymbolError(symbol, candSymbol)
        else:
            symbol = Symbol(parent=parentSymbol, identifier=identifier,
                            templateParams=templateParams,
                            templateArgs=templateArgs,
                            declaration=declaration,
                            docname=docname)
        return symbol