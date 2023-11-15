    def add_target_and_index(self, ast, sig, signode):
        ids = [ # the newest should be first
               ast.get_id_v2(),
               ast.get_id_v1()
               ]
        theid = ids[0]
        ast.newestId = theid
        assert theid # shouldn't be None
        name = text_type(ast.prefixedName)
        if theid not in self.state.document.ids:
            # if the name is not unique, the first one will win
            objects = self.env.domaindata['cpp']['objects']
            if name not in objects:
                signode['names'].append(name)
            else:
                pass
                #print("[CPP] non-unique name:", name)
            for id in ids:
                if id: # is None when the element didn't exist in that version
                    signode['ids'].append(id)
            signode['first'] = (not self.names)
            self.state.document.note_explicit_target(signode)
            if not name in objects:
                objects.setdefault(name, (self.env.docname, ast))
                if ast.objectType == 'enumerator':
                    # find the parent, if it exists && is an enum
                    #                     && it's unscoped,
                    #                  then add the name to the parent scope
                    assert len(ast.prefixedName.names) > 0
                    parentPrefixedAstName = ASTNestedName(ast.prefixedName.names[:-1])
                    parentPrefixedName = text_type(parentPrefixedAstName)
                    if parentPrefixedName in objects:
                        docname, parentAst = objects[parentPrefixedName]
                        if parentAst.objectType == 'enum' and not parentAst.scoped:
                            enumeratorName = ASTNestedName([ast.prefixedName.names[-1]])
                            assert len(parentAst.prefixedName.names) > 0
                            enumScope = ASTNestedName(parentAst.prefixedName.names[:-1])
                            unscopedName = enumeratorName.prefix_nested_name(enumScope)
                            txtUnscopedName = text_type(unscopedName)
                            if not txtUnscopedName in objects:
                                objects.setdefault(txtUnscopedName,
                                                   (self.env.docname, ast))
                # add the uninstantiated template if it doesn't exist
                uninstantiated = ast.prefixedName.get_name_no_last_template()
                if uninstantiated != name and uninstantiated not in objects:
                    signode['names'].append(uninstantiated)
                    objects.setdefault(uninstantiated, (self.env.docname, ast))
            self.env.ref_context['cpp:lastname'] = ast.prefixedName

        indextext = self.get_index_text(name)
        if not re.compile(r'^[a-zA-Z0-9_]*$').match(theid):
            self.state_machine.reporter.warning(
                'Index id generation for C++ object "%s" failed, please '
                'report as bug (id=%s).' % (text_type(ast), theid),
                line=self.lineno)
        self.indexnode['entries'].append(('single', indextext, theid, ''))