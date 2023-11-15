    def _apply_solver(self):
        if not self._save_results:
            for block in self._pyomo_model.block_data_objects(descend_into=True, active=True):
                for var in block.component_data_objects(ctype=pyomo.core.base.var.Var, descend_into=False, active=True, sort=False):
                    var.stale = True
        _log_file = self._log_file
        if self.version() >= (12, 10):
            _log_file = open(self._log_file, 'w')
        try:
            if self._tee:
                def _process_stream(arg):
                    sys.stdout.write(arg)
                    return arg
                self._solver_model.set_results_stream(_log_file, _process_stream)
            else:
                self._solver_model.set_results_stream(_log_file)
            
            if self._keepfiles:
                print("Solver log file: "+self._log_file)
            
            obj_degree = self._objective.expr.polynomial_degree()
            if obj_degree is None or obj_degree > 2:
                raise DegreeError('CPLEXDirect does not support expressions of degree {0}.'\
                                  .format(obj_degree))
            elif obj_degree == 2:
                quadratic_objective = True
            else:
                quadratic_objective = False
            
            num_integer_vars = self._solver_model.variables.get_num_integer()
            num_binary_vars = self._solver_model.variables.get_num_binary()
            num_sos = self._solver_model.SOS.get_num()
            
            if self._solver_model.quadratic_constraints.get_num() != 0:
                quadratic_cons = True
            else:
                quadratic_cons = False
            
            if (num_integer_vars + num_binary_vars + num_sos) > 0:
                integer = True
            else:
                integer = False
            
            if integer:
                if quadratic_cons:
                    self._solver_model.set_problem_type(self._solver_model.problem_type.MIQCP)
                elif quadratic_objective:
                    self._solver_model.set_problem_type(self._solver_model.problem_type.MIQP)
                else:
                    self._solver_model.set_problem_type(self._solver_model.problem_type.MILP)
            else:
                if quadratic_cons:
                    self._solver_model.set_problem_type(self._solver_model.problem_type.QCP)
                elif quadratic_objective:
                    self._solver_model.set_problem_type(self._solver_model.problem_type.QP)
                else:
                    self._solver_model.set_problem_type(self._solver_model.problem_type.LP)
            
            for key, option in self.options.items():
                opt_cmd = self._solver_model.parameters
                key_pieces = key.split('_')
                for key_piece in key_pieces:
                    opt_cmd = getattr(opt_cmd, key_piece)
                # When options come from the pyomo command, all
                # values are string types, so we try to cast
                # them to a numeric value in the event that
                # setting the parameter fails.
                try:
                    opt_cmd.set(option)
                except self._cplex.exceptions.CplexError:
                    # we place the exception handling for
                    # checking the cast of option to a float in
                    # another function so that we can simply
                    # call raise here instead of except
                    # TypeError as e / raise e, because the
                    # latter does not preserve the Cplex stack
                    # trace
                    if not _is_numeric(option):
                        raise
                    opt_cmd.set(float(option))
            
            t0 = time.time()
            self._solver_model.solve()
            t1 = time.time()
            self._wallclock_time = t1 - t0
        finally:
            if self.version() >= (12, 10):
                _log_file.close()

        # FIXME: can we get a return code indicating if CPLEX had a significant failure?
        return Bunch(rc=None, log=None)