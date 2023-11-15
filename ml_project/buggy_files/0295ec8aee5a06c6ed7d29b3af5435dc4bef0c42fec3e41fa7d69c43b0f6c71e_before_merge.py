    def find_name(self, nestedName, templateDecls, templateShorthand, matchSelf):
        # type: (Any, Any, Any, bool) -> Symbol
        # templateShorthand: missing template parameter lists for templates is ok

        # TODO: unify this with the _add_symbols
        # This condition should be checked at the parser level.
        assert len(templateDecls) <= nestedName.num_templates() + 1
        parentSymbol = self
        if nestedName.rooted:
            while parentSymbol.parent:
                parentSymbol = parentSymbol.parent
        names = nestedName.names

        # walk up until we find the first identifier
        firstName = names[0]
        if not firstName.is_operator():
            while parentSymbol.parent:
                if parentSymbol.find_identifier(firstName.identifier,
                                                matchSelf=matchSelf):
                    break
                parentSymbol = parentSymbol.parent

        iTemplateDecl = 0
        for iName in range(len(names)):
            name = names[iName]
            if iName + 1 == len(names):
                if name.is_operator():
                    identifier = None
                    templateArgs = None
                    operator = name
                else:
                    identifier = name.identifier
                    templateArgs = name.templateArgs
                    operator = None
                if iTemplateDecl < len(templateDecls):
                    assert iTemplateDecl + 1 == len(templateDecls)
                    templateParams = templateDecls[iTemplateDecl]
                else:
                    assert iTemplateDecl == len(templateDecls)
                    templateParams = None
                symbol = parentSymbol._find_named_symbol(identifier,
                                                         templateParams,
                                                         templateArgs,
                                                         operator,
                                                         templateShorthand=templateShorthand,
                                                         matchSelf=matchSelf)
                if symbol:
                    return symbol
                else:
                    return None
            else:
                # there shouldn't be anything inside an operator
                assert not name.is_operator()
                identifier = name.identifier
                templateArgs = name.templateArgs
                if templateArgs and iTemplateDecl < len(templateDecls):
                    templateParams = templateDecls[iTemplateDecl]
                    iTemplateDecl += 1
                else:
                    templateParams = None
                symbol = parentSymbol._find_named_symbol(identifier,
                                                         templateParams,
                                                         templateArgs,
                                                         operator=None,
                                                         templateShorthand=templateShorthand,
                                                         matchSelf=matchSelf)
                if symbol is None:
                    # TODO: maybe search without template args
                    return None
                # We have now matched part of a nested name, and need to match more
                # so even if we should matchSelf before, we definitely shouldn't
                # even more. (see also issue #2666)
                matchSelf = False
            parentSymbol = symbol
        assert False  # should have returned in the loop