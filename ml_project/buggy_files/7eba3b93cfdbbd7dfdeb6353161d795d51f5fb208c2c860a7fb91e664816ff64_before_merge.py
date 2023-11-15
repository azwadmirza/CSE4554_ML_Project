    def _resolve_xref_inner(self, env, fromdocname, builder, typ,
                            target, node, contnode, emitWarnings=True):
        # type: (BuildEnvironment, unicode, Builder, unicode, unicode, nodes.Node, nodes.Node, bool) -> nodes.Node  # NOQA

        class Warner(object):
            def warn(self, msg):
                if emitWarnings:
                    logger.warning(msg, location=node)
        warner = Warner()
        # add parens again for those that could be functions
        if typ == 'any' or typ == 'func':
            target += '()'
        parser = DefinitionParser(target, warner, env.config)
        try:
            ast, isShorthand = parser.parse_xref_object()
            parser.assert_end()
        except DefinitionError as e:
            def findWarning(e):  # as arg to stop flake8 from complaining
                if typ != 'any' and typ != 'func':
                    return target, e
                # hax on top of the paren hax to try to get correct errors
                parser2 = DefinitionParser(target[:-2], warner, env.config)
                try:
                    parser2.parse_xref_object()
                    parser2.assert_end()
                except DefinitionError as e2:
                    return target[:-2], e2
                # strange, that we don't get the error now, use the original
                return target, e
            t, ex = findWarning(e)
            warner.warn('Unparseable C++ cross-reference: %r\n%s'
                        % (t, text_type(ex.description)))
            return None, None
        parentKey = node.get("cpp:parent_key", None)
        rootSymbol = self.data['root_symbol']
        if parentKey:
            parentSymbol = rootSymbol.direct_lookup(parentKey)
            if not parentSymbol:
                print("Target: ", target)
                print("ParentKey: ", parentKey)
                print(rootSymbol.dump(1))
            assert parentSymbol  # should be there
        else:
            parentSymbol = rootSymbol

        if isShorthand:
            ns = ast  # type: ASTNamespace
            name = ns.nestedName
            if ns.templatePrefix:
                templateDecls = ns.templatePrefix.templates
            else:
                templateDecls = []
            s = parentSymbol.find_name(name, templateDecls, typ,
                                       templateShorthand=True,
                                       matchSelf=True, recurseInAnon=True)
        else:
            decl = ast  # type: ASTDeclaration
            s = parentSymbol.find_declaration(decl, typ,
                                              templateShorthand=True,
                                              matchSelf=True, recurseInAnon=True)
        if s is None or s.declaration is None:
            txtName = text_type(name)
            if txtName.startswith('std::') or txtName == 'std':
                raise NoUri()
            return None, None

        if typ.startswith('cpp:'):
            typ = typ[4:]
        if typ == 'func':
            typ = 'function'
        declTyp = s.declaration.objectType

        def checkType():
            if typ == 'any' or typ == 'identifier':
                return True
            if declTyp == 'templateParam':
                return True
            objtypes = self.objtypes_for_role(typ)
            if objtypes:
                return declTyp in objtypes
            print("Type is %s, declType is %s" % (typ, declTyp))
            assert False
        if not checkType():
            warner.warn("cpp:%s targets a %s (%s)."
                        % (typ, s.declaration.objectType,
                           s.get_full_nested_name()))

        declaration = s.declaration
        if isShorthand:
            fullNestedName = s.get_full_nested_name()
            displayName = fullNestedName.get_display_string().lstrip(':')
        else:
            displayName = decl.get_display_string()
        docname = s.docname
        assert docname

        # the non-identifier refs are cross-references, which should be processed:
        # - fix parenthesis due to operator() and add_function_parentheses
        if typ != "identifier":
            title = contnode.pop(0).astext()
            # If it's operator(), we need to add '()' if explicit function parens
            # are requested. Then the Sphinx machinery will add another pair.
            # Also, if it's an 'any' ref that resolves to a function, we need to add
            # parens as well.
            # However, if it's a non-shorthand function ref, for a function that
            # takes no arguments, then we may need to add parens again as well.
            addParen = 0
            if not node.get('refexplicit', False) and declaration.objectType == 'function':
                if isShorthand:
                    # this is just the normal haxing for 'any' roles
                    if env.config.add_function_parentheses and typ == 'any':
                        addParen += 1
                    # and now this stuff for operator()
                    if (env.config.add_function_parentheses and typ == 'function' and
                            title.endswith('operator()')):
                        addParen += 1
                    if ((typ == 'any' or typ == 'function') and
                            title.endswith('operator') and
                            displayName.endswith('operator()')):
                        addParen += 1
                else:
                    # our job here is to essentially nullify add_function_parentheses
                    if env.config.add_function_parentheses:
                        if typ == 'any' and displayName.endswith('()'):
                            addParen += 1
                        elif typ == 'function':
                            if title.endswith('()') and not displayName.endswith('()'):
                                title = title[:-2]
                    else:
                        if displayName.endswith('()'):
                            addParen += 1
            if addParen > 0:
                title += '()' * addParen
            # and reconstruct the title again
            contnode += nodes.Text(title)
        return make_refnode(builder, fromdocname, docname,
                            declaration.get_newest_id(), contnode, displayName
                            ), declaration.objectType