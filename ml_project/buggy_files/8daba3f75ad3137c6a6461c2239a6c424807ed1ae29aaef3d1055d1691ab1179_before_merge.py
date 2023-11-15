    def _hook_register_write(self, state):

        reg_write_offset = state.inspect.reg_write_offset

        if reg_write_offset == state.arch.sp_offset:
            # it's updating stack pointer. skip
            return

        reg_write_expr = state.inspect.reg_write_expr
        reg_write_length = len(reg_write_expr) // 8

        # annotate it
        # reg_write_expr = reg_write_expr.annotate(VariableSourceAnnotation.from_state(state))

        state.inspect.reg_write_expr = reg_write_expr

        existing_vars = self.variable_manager[self.func_addr].find_variables_by_stmt(state.scratch.bbl_addr,
                                                                                     state.scratch.stmt_idx,
                                                                                     'register')
        if not existing_vars:
            # create the variable
            variable = SimRegisterVariable(reg_write_offset, reg_write_length,
                                           ident=self.variable_manager[self.func_addr].next_variable_ident('register'),
                                           region=self.func_addr,
                                           )
            var_offset = self._normalize_register_offset(reg_write_offset)
            self.register_region.set_variable(var_offset, variable)
            # record this variable in variable manager
            self.variable_manager[self.func_addr].set_variable('register', var_offset, variable)
            self.variable_manager[self.func_addr].write_to(variable, 0, self._codeloc_from_state(state))

        # is it writing a pointer to a stack variable into the register?
        # e.g. lea eax, [ebp-0x40]
        stack_offset = self._addr_to_stack_offset(reg_write_expr)
        if stack_offset is not None:
            # it is!
            # unfortunately we don't know the size. We use size None for now.

            if stack_offset not in self.stack_region:
                lea_size = 1
                new_var = SimStackVariable(stack_offset, lea_size, base='bp',
                                            ident=self.variable_manager[self.func_addr].next_variable_ident('stack'),
                                            region=self.func_addr,
                                            )
                self.stack_region.add_variable(stack_offset, new_var)

                # record this variable in variable manager
                self.variable_manager[self.func_addr].add_variable('stack', stack_offset, new_var)

            base_offset = self.stack_region.get_base_addr(stack_offset)
            assert base_offset is not None
            for var in self.stack_region.get_variables_by_offset(stack_offset):
                self.variable_manager[self.func_addr].reference_at(var, stack_offset - base_offset,
                                                                   self._codeloc_from_state(state)
                                                                   )