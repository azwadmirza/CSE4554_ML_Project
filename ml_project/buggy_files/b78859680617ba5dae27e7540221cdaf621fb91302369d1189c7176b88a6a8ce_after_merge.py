    def add_target_and_index(self, ast, sig, signode):
        # general note: name must be lstrip(':')'ed, to remove "::"
        try:
            id_v1 = ast.get_id_v1()
        except NoOldIdError:
            id_v1 = None
        id_v2 = ast.get_id_v2()
        # store them in reverse order, so the newest is first
        ids  = [id_v2, id_v1]

        theid = ids[0]
        ast.newestId = theid
        assert theid  # shouldn't be None
        name = text_type(ast.prefixedName).lstrip(':')
        if theid not in self.state.document.ids:
            # if the name is not unique, the first one will win
            objects = self.env.domaindata['cpp']['objects']
            if name not in objects:
                signode['names'].append(name)
            else:
                pass
                # print("[CPP] non-unique name:", name)
            for id in ids:
                if id:  # is None when the element didn't exist in that version
                    signode['ids'].append(id)
            signode['first'] = (not self.names)
            self.state.document.note_explicit_target(signode)
            if name not in objects:
                objects.setdefault(name, (self.env.docname, ast))
                if ast.objectType == 'enumerator':
                    self._add_enumerator_to_parent(ast, objects)
                # add the uninstantiated template if it doesn't exist
                uninstantiated = ast.prefixedName.get_name_no_last_template().lstrip(':')
                if uninstantiated != name and uninstantiated not in objects:
                    signode['names'].append(uninstantiated)
                    objects.setdefault(uninstantiated, (self.env.docname, ast))

        indextext = self.get_index_text(name)
        if not re.compile(r'^[a-zA-Z0-9_]*$').match(theid):
            self.state_machine.reporter.warning(
                'Index id generation for C++ object "%s" failed, please '
                'report as bug (id=%s).' % (text_type(ast), theid),
                line=self.lineno)
        self.indexnode['entries'].append(('single', indextext, theid, ''))