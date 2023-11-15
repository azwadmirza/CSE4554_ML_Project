    def _hook_register_read(self, state):

        reg_read_offset = state.inspect.reg_read_offset
        reg_read_length = state.inspect.reg_read_length

        if reg_read_offset == state.arch.sp_offset and reg_read_length == state.arch.bytes:
            # TODO: make sure the sp is not overwritten by something that we are not tracking
            return

        #if reg_read_offset == state.arch.bp_offset and reg_read_length == state.arch.bytes:
        #    # TODO:

        var_offset = self._normalize_register_offset(reg_read_offset)
        if var_offset not in self.register_region:
            # the variable being read doesn't exist before
            variable = SimRegisterVariable(reg_read_offset, reg_read_length,
                                           ident=self.variable_manager[self.func_addr].next_variable_ident('register'),
                                           region=self.func_addr,
                                           )
            self.register_region.add_variable(var_offset, variable)

            # record this variable in variable manager
            self.variable_manager[self.func_addr].add_variable('register', var_offset, variable)