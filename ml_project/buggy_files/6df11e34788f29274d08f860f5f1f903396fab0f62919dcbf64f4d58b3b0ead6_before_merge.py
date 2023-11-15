    def _add_symbols(self, nestedName, templateDecls, declaration, docname):
        # type: (ASTNestedName, List[Any], ASTDeclaration, unicode) -> Symbol
        # Used for adding a whole path of symbols, where the last may or may not
        # be an actual declaration.

        def onMissingQualifiedSymbol(parentSymbol, identOrOp, templateParams, templateArgs):
            # type: (Symbol, Union[ASTIdentifier, ASTOperator], Any, ASTTemplateArgs) -> Symbol
            return Symbol(parent=parentSymbol, identOrOp=identOrOp,
                          templateParams=templateParams,
                          templateArgs=templateArgs, declaration=None,
                          docname=None)

        lookupResult = self._symbol_lookup(nestedName, templateDecls,
                                           onMissingQualifiedSymbol,
                                           strictTemplateParamArgLists=True,
                                           ancestorLookupType=None,
                                           templateShorthand=False,
                                           matchSelf=False,
                                           recurseInAnon=True,
                                           correctPrimaryTemplateArgs=True)
        assert lookupResult is not None  # we create symbols all the way, so that can't happen
        # TODO: actually do the iteration over results, though let's find a test case first
        try:
            symbol = next(lookupResult.symbols)
        except StopIteration:
            symbol = None

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
            # It may simply be a function overload, so let's compare ids.
            isRedeclaration = True
            candSymbol = Symbol(parent=lookupResult.parentSymbol,
                                identOrOp=lookupResult.identOrOp,
                                templateParams=lookupResult.templateParams,
                                templateArgs=lookupResult.templateArgs,
                                declaration=declaration,
                                docname=docname)
            if declaration.objectType == "function":
                newId = declaration.get_newest_id()
                oldId = symbol.declaration.get_newest_id()
                if newId != oldId:
                    # we already inserted the symbol, so return the new one
                    symbol = candSymbol
                    isRedeclaration = False
            if isRedeclaration:
                # Redeclaration of the same symbol.
                # Let the new one be there, but raise an error to the client
                # so it can use the real symbol as subscope.
                # This will probably result in a duplicate id warning.
                candSymbol.isRedeclaration = True
                raise _DuplicateSymbolError(symbol, declaration)
        else:
            symbol = Symbol(parent=lookupResult.parentSymbol,
                            identOrOp=lookupResult.identOrOp,
                            templateParams=lookupResult.templateParams,
                            templateArgs=lookupResult.templateArgs,
                            declaration=declaration,
                            docname=docname)
        return symbol