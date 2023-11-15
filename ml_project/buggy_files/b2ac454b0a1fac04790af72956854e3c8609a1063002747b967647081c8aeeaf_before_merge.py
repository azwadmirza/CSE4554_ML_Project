    def compile_roles_handlers(self):
        '''
        Handles the role handler compilation step, returning a flat list of Handlers
        This is done for all roles in the Play.
        '''

        block_list = []

        if len(self.roles) > 0:
            for r in self.roles:
                block_list.extend(r.get_handler_blocks(play=self))

        return block_list