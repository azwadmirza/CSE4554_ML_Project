    def solve(self, problem: QuadraticProgram) -> ADMMOptimizationResult:
        """Tries to solves the given problem using ADMM algorithm.

        Args:
            problem: The problem to be solved.

        Returns:
            The result of the optimizer applied to the problem.

        Raises:
            QiskitOptimizationError: If the problem is not compatible with the ADMM optimizer.
        """
        self._verify_compatibility(problem)

        # debug
        self._log.debug("Initial problem: %s", problem.export_as_lp_string())

        # map integer variables to binary variables
        from ..converters.integer_to_binary import IntegerToBinary
        int2bin = IntegerToBinary()
        original_variables = problem.variables
        problem = int2bin.convert(problem)

        # we deal with minimization in the optimizer, so turn the problem to minimization
        problem, sense = self._turn_to_minimization(problem)

        # create our computation state.
        self._state = ADMMState(problem, self._params.rho_initial)

        # parse problem and convert to an ADMM specific representation.
        self._state.binary_indices = self._get_variable_indices(problem, Variable.Type.BINARY)
        self._state.continuous_indices = self._get_variable_indices(problem,
                                                                    Variable.Type.CONTINUOUS)
        if self._params.warm_start:
            # warm start injection for the initial values of the variables
            self._warm_start(problem)

        # convert optimization problem to a set of matrices and vector that are used
        # at each iteration.
        self._convert_problem_representation()

        start_time = time.time()
        # we have not stated our computations yet, so elapsed time initialized as zero.
        elapsed_time = 0.0
        iteration = 0
        residual = 1.e+2

        while (iteration < self._params.maxiter and residual > self._params.tol) \
                and (elapsed_time < self._params.max_time):
            if self._state.step1_absolute_indices:
                op1 = self._create_step1_problem()
                self._state.x0 = self._update_x0(op1)
                # debug
                self._log.debug("Step 1 sub-problem: %s", op1.export_as_lp_string())
            # else, no binary variables exist, and no update to be done in this case.
            # debug
            self._log.debug("x0=%s", self._state.x0)

            op2 = self._create_step2_problem()
            self._state.u, self._state.z = self._update_x1(op2)
            # debug
            self._log.debug("Step 2 sub-problem: %s", op2.export_as_lp_string())
            self._log.debug("u=%s", self._state.u)
            self._log.debug("z=%s", self._state.z)

            if self._params.three_block:
                if self._state.binary_indices:
                    op3 = self._create_step3_problem()
                    self._state.y = self._update_y(op3)
                    # debug
                    self._log.debug("Step 3 sub-problem: %s", op3.export_as_lp_string())
                # debug
                self._log.debug("y=%s", self._state.y)

            self._state.lambda_mult = self._update_lambda_mult()
            # debug
            self._log.debug("lambda: %s", self._state.lambda_mult)

            cost_iterate = self._get_objective_value()
            constraint_residual = self._get_constraint_residual()
            residual, dual_residual = self._get_solution_residuals(iteration)
            merit = self._get_merit(cost_iterate, constraint_residual)
            # debug
            self._log.debug("cost_iterate=%s, cr=%s, merit=%s",
                            cost_iterate, constraint_residual, merit)

            # costs are saved with their original sign.
            self._state.cost_iterates.append(cost_iterate)
            self._state.residuals.append(residual)
            self._state.dual_residuals.append(dual_residual)
            self._state.cons_r.append(constraint_residual)
            self._state.merits.append(merit)
            self._state.lambdas.append(np.linalg.norm(self._state.lambda_mult))

            self._state.x0_saved.append(self._state.x0)
            self._state.u_saved.append(self._state.u)
            self._state.z_saved.append(self._state.z)
            self._state.z_saved.append(self._state.y)

            self._update_rho(residual, dual_residual)

            iteration += 1
            elapsed_time = time.time() - start_time

        binary_vars, continuous_vars, objective_value = self._get_best_merit_solution()
        solution = self._revert_solution_indexes(binary_vars, continuous_vars)

        # flip the objective sign again if required
        objective_value = objective_value * sense

        # convert back integer to binary
        base_result = OptimizationResult(solution, objective_value, original_variables,
                                         OptimizationResultStatus.SUCCESS)
        base_result = int2bin.interpret(base_result)

        # third parameter is our internal state of computations.
        result = ADMMOptimizationResult(x=base_result.x, fval=base_result.fval,
                                        variables=base_result.variables,
                                        state=self._state,
                                        status=self._get_feasibility_status(problem, base_result.x))

        # debug
        self._log.debug("solution=%s, objective=%s at iteration=%s",
                        solution, objective_value, iteration)
        return result