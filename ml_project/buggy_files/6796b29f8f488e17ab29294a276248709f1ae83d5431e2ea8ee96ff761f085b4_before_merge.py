    def _analyze_function(self) -> Optional[SimCC]:
        """
        Go over the variable information in variable manager for this function, and return all uninitialized
        register/stack variables.
        """

        if self._function.is_simprocedure or self._function.is_plt:
            # we do not analyze SimProcedures or PLT stubs
            return None

        if not self._variable_manager.has_function_manager:
            l.warning("Please run variable recovery on %r before analyzing its calling convention.", self._function)
            return None

        vm = self._variable_manager[self._function.addr]

        input_variables = vm.input_variables()

        input_args = self._args_from_vars(input_variables)

        # TODO: properly determine sp_delta
        sp_delta = self.project.arch.bytes if self.project.arch.call_pushes_ret else 0

        cc = SimCC.find_cc(self.project.arch, list(input_args), sp_delta)

        if cc is None:
            l.warning('_analyze_function(): Cannot find a calling convention for %r that fits the given arguments.',
                      self._function)
        else:
            # reorder args
            args = self._reorder_args(input_args, cc)
            cc.args = args

            # set return value
            cc.ret_val = cc.return_val

        return cc