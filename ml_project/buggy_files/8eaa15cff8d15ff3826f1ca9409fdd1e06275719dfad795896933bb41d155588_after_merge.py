    def get_block_list(self, play=None, variable_manager=None, loader=None):

        # only need play passed in when dynamic
        if play is None:
            myplay =  self._parent._play
        else:
            myplay = play

        ri = RoleInclude.load(self._role_name, play=myplay, variable_manager=variable_manager, loader=loader)
        ri.vars.update(self.vars)

        # build role
        actual_role = Role.load(ri, myplay, parent_role=self._parent_role, from_files=self._from_files)
        actual_role._metadata.allow_duplicates = self.allow_duplicates

        # compile role with parent roles as dependencies to ensure they inherit
        # variables
        if not self._parent_role:
            dep_chain = []
        else:
            dep_chain = list(self._parent_role._parents)
            dep_chain.append(self._parent_role)

        blocks = actual_role.compile(play=myplay, dep_chain=dep_chain)
        for b in blocks:
            b._parent = self

        # updated available handlers in play
        handlers = actual_role.get_handler_blocks(play=myplay)
        myplay.handlers = myplay.handlers + handlers
        return blocks, handlers