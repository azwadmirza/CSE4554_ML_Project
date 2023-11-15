    def generate_execution_code(self, code):
        """
        Generate code in the following steps

            1)  copy any closure variables determined thread-private
                into temporaries

            2)  allocate temps for start, stop and step

            3)  generate a loop that calculates the total number of steps,
                which then computes the target iteration variable for every step:

                    for i in prange(start, stop, step):
                        ...

                becomes

                    nsteps = (stop - start) / step;
                    i = start;

                    #pragma omp parallel for lastprivate(i)
                    for (temp = 0; temp < nsteps; temp++) {
                        i = start + step * temp;
                        ...
                    }

                Note that accumulation of 'i' would have a data dependency
                between iterations.

                Also, you can't do this

                    for (i = start; i < stop; i += step)
                        ...

                as the '<' operator should become '>' for descending loops.
                'for i from x < i < y:' does not suffer from this problem
                as the relational operator is known at compile time!

            4) release our temps and write back any private closure variables
        """
        self.declare_closure_privates(code)

        # This can only be a NameNode
        target_index_cname = self.target.entry.cname

        # This will be used as the dict to format our code strings, holding
        # the start, stop , step, temps and target cnames
        fmt_dict = {
            'target': target_index_cname,
            'target_type': self.target.type.empty_declaration_code()
        }

        # Setup start, stop and step, allocating temps if needed
        start_stop_step = self.start, self.stop, self.step
        defaults = '0', '0', '1'
        for node, name, default in zip(start_stop_step, self.names, defaults):
            if node is None:
                result = default
            elif node.is_literal:
                result = node.get_constant_c_result_code()
            else:
                node.generate_evaluation_code(code)
                result = node.result()

            fmt_dict[name] = result

        fmt_dict['i'] = code.funcstate.allocate_temp(self.index_type, False)
        fmt_dict['nsteps'] = code.funcstate.allocate_temp(self.index_type, False)

        # TODO: check if the step is 0 and if so, raise an exception in a
        # 'with gil' block. For now, just abort
        code.putln("if (%(step)s == 0) abort();" % fmt_dict)

        self.setup_parallel_control_flow_block(code) # parallel control flow block

        self.control_flow_var_code_point = code.insertion_point()

        # Note: nsteps is private in an outer scope if present
        code.putln("%(nsteps)s = (%(stop)s - %(start)s + %(step)s - %(step)s/abs(%(step)s)) / %(step)s;" % fmt_dict)

        # The target iteration variable might not be initialized, do it only if
        # we are executing at least 1 iteration, otherwise we should leave the
        # target unaffected. The target iteration variable is firstprivate to
        # shut up compiler warnings caused by lastprivate, as the compiler
        # erroneously believes that nsteps may be <= 0, leaving the private
        # target index uninitialized
        code.putln("if (%(nsteps)s > 0)" % fmt_dict)
        code.begin_block() # if block
        self.generate_loop(code, fmt_dict)
        code.end_block() # end if block

        self.restore_labels(code)

        if self.else_clause:
            if self.breaking_label_used:
                code.put("if (%s < 2)" % Naming.parallel_why)

            code.begin_block() # else block
            code.putln("/* else */")
            self.else_clause.generate_execution_code(code)
            code.end_block() # end else block

        # ------ cleanup ------
        self.end_parallel_control_flow_block(code) # end parallel control flow block

        # And finally, release our privates and write back any closure
        # variables
        for temp in start_stop_step + (self.chunksize, self.num_threads):
            if temp is not None:
                temp.generate_disposal_code(code)
                temp.free_temps(code)

        code.funcstate.release_temp(fmt_dict['i'])
        code.funcstate.release_temp(fmt_dict['nsteps'])

        self.release_closure_privates(code)