    def _add_symbols(self, nestedName, templateDecls, declaration, docname):
        # type: (ASTNestedName, List[Any], ASTDeclaration, unicode) -> Symbol
        # Used for adding a whole path of symbols, where the last may or may not
        # be an actual declaration.

        if Symbol.debug_lookup:
            print("_add_symbols:")
            print("   tdecls:", templateDecls)
            print("   nn:    ", nestedName)
            print("   decl:  ", declaration)
            print("   doc:   ", docname)

        def onMissingQualifiedSymbol(parentSymbol, identOrOp, templateParams, templateArgs):
            # type: (Symbol, Union[ASTIdentifier, ASTOperator], Any, ASTTemplateArgs) -> Symbol
            if Symbol.debug_lookup:
                print("   _add_symbols, onMissingQualifiedSymbol:")
                print("      templateParams:", templateParams)
                print("      identOrOp:     ", identOrOp)
                print("      templateARgs:  ", templateArgs)
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
        symbols = list(lookupResult.symbols)
        if len(symbols) == 0:
            if Symbol.debug_lookup:
                print("   _add_symbols, result, no symbol:")
                print("      templateParams:", lookupResult.templateParams)
                print("      identOrOp:     ", lookupResult.identOrOp)
                print("      templateArgs:  ", lookupResult.templateArgs)
                print("      declaration:   ", declaration)
                print("      docname:       ", docname)
            symbol = Symbol(parent=lookupResult.parentSymbol,
                            identOrOp=lookupResult.identOrOp,
                            templateParams=lookupResult.templateParams,
                            templateArgs=lookupResult.templateArgs,
                            declaration=declaration,
                            docname=docname)
            return symbol

        if Symbol.debug_lookup:
            print("   _add_symbols, result, symbols:")
            print("      number symbols:", len(symbols))

        if not declaration:
            if Symbol.debug_lookup:
                print("      no delcaration")
            # good, just a scope creation
            # TODO: what if we have more than one symbol?
            return symbols[0]

        noDecl = []
        withDecl = []
        dupDecl = []
        for s in symbols:
            if s.declaration is None:
                noDecl.append(s)
            elif s.isRedeclaration:
                dupDecl.append(s)
            else:
                withDecl.append(s)
        if Symbol.debug_lookup:
            print("      #noDecl:  ", len(noDecl))
            print("      #withDecl:", len(withDecl))
            print("      #dupDecl: ", len(dupDecl))
        # With partial builds we may start with a large symbol tree stripped of declarations.
        # Essentially any combination of noDecl, withDecl, and dupDecls seems possible.
        # TODO: make partial builds fully work. What should happen when the primary symbol gets
        #  deleted, and other duplicates exist? The full document should probably be rebuild.

        # First check if one of those with a declaration matches.
        # If it's a function, we need to compare IDs,
        # otherwise there should be only one symbol with a declaration.
        def makeCandSymbol():
            if Symbol.debug_lookup:
                print("      begin: creating candidate symbol")
            symbol = Symbol(parent=lookupResult.parentSymbol,
                            identOrOp=lookupResult.identOrOp,
                            templateParams=lookupResult.templateParams,
                            templateArgs=lookupResult.templateArgs,
                            declaration=declaration,
                            docname=docname)
            if Symbol.debug_lookup:
                print("      end:   creating candidate symbol")
            return symbol
        if len(withDecl) == 0:
            candSymbol = None
        else:
            candSymbol = makeCandSymbol()

            def handleDuplicateDeclaration(symbol, candSymbol):
                if Symbol.debug_lookup:
                    print("      redeclaration")
                # Redeclaration of the same symbol.
                # Let the new one be there, but raise an error to the client
                # so it can use the real symbol as subscope.
                # This will probably result in a duplicate id warning.
                candSymbol.isRedeclaration = True
                raise _DuplicateSymbolError(symbol, declaration)

            if declaration.objectType != "function":
                assert len(withDecl) <= 1
                handleDuplicateDeclaration(withDecl[0], candSymbol)
                # (not reachable)

            # a function, so compare IDs
            candId = declaration.get_newest_id()
            if Symbol.debug_lookup:
                print("      candId:", candId)
            for symbol in withDecl:
                oldId = symbol.declaration.get_newest_id()
                if Symbol.debug_lookup:
                    print("      oldId: ", oldId)
                if candId == oldId:
                    handleDuplicateDeclaration(symbol, candSymbol)
                    # (not reachable)
            # no candidate symbol found with matching ID
        # if there is an empty symbol, fill that one
        if len(noDecl) == 0:
            if Symbol.debug_lookup:
                print("      no match, no empty, candSybmol is not None?:", candSymbol is not None)  # NOQA
            if candSymbol is not None:
                return candSymbol
            else:
                return makeCandSymbol()
        else:
            if Symbol.debug_lookup:
                print("      no match, but fill an empty declaration, candSybmol is not None?:", candSymbol is not None)  # NOQA
            if candSymbol is not None:
                candSymbol.remove()
            # assert len(noDecl) == 1
            # TODO: enable assertion when we at some point find out how to do cleanup
            # for now, just take the first one, it should work fine ... right?
            symbol = noDecl[0]
            # If someone first opened the scope, and then later
            # declares it, e.g,
            # .. namespace:: Test
            # .. namespace:: nullptr
            # .. class:: Test
            symbol._fill_empty(declaration, docname)
            return symbol