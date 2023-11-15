    def solve(self, problem: QuadraticProgram) -> OptimizationResult:
        """Tries to solve the given problem using the recursive optimizer.

        Runs the optimizer to try to solve the optimization problem.

        Args:
            problem: The problem to be solved.

        Returns:
            The result of the optimizer applied to the problem.

        Raises:
            QiskitOptimizationError: Incompatible problem.
            QiskitOptimizationError: Infeasible due to variable substitution
        """
        # check compatibility and raise exception if incompatible
        msg = self.get_compatibility_msg(problem)
        if len(msg) > 0:
            raise QiskitOptimizationError('Incompatible problem: {}'.format(msg))

        # convert problem to QUBO, this implicitly checks if the problem is compatible
        qubo_converter = QuadraticProgramToQubo()
        problem_ = qubo_converter.encode(problem)
        problem_ref = deepcopy(problem_)

        # run recursive optimization until the resulting problem is small enough
        replacements = {}
        while problem_.get_num_vars() > self._min_num_vars:

            # solve current problem with optimizer
            result = self._min_eigen_optimizer.solve(problem_)

            # analyze results to get strongest correlation
            correlations = result.get_correlations()
            i, j = self._find_strongest_correlation(correlations)

            x_i = problem_.variables[i].name
            x_j = problem_.variables[j].name
            if correlations[i, j] > 0:
                # set x_i = x_j
                problem_.substitute_variables()
                problem_ = problem_.substitute_variables(variables={i: (j, 1)})
                if problem_.status == QuadraticProgram.Status.INFEASIBLE:
                    raise QiskitOptimizationError('Infeasible due to variable substitution')
                replacements[x_i] = (x_j, 1)
            else:
                # set x_i = 1 - x_j, this is done in two steps:
                # 1. set x_i = 1 + x_i
                # 2. set x_i = -x_j

                # 1a. get additional offset
                constant = problem_.objective.constant
                constant += problem_.objective.quadratic[i, i]
                constant += problem_.objective.linear[i]
                problem_.objective.constant = constant

                # 1b. get additional linear part
                for k in range(problem_.get_num_vars()):
                    coeff = problem_.objective.quadratic[i, k]
                    if np.abs(coeff) > 1e-10:
                        coeff += problem_.objective.linear[k]
                        problem_.objective.linear[k] = coeff

                # 2. replace x_i by -x_j
                problem_ = problem_.substitute_variables(variables={i: (j, -1)})
                if problem_.status == QuadraticProgram.Status.INFEASIBLE:
                    raise QiskitOptimizationError('Infeasible due to variable substitution')
                replacements[x_i] = (x_j, -1)

        # solve remaining problem
        result = self._min_num_vars_optimizer.solve(problem_)

        # unroll replacements
        var_values = {}
        for i, x in enumerate(problem_.variables):
            var_values[x.name] = result.x[i]

        def find_value(x, replacements, var_values):
            if x in var_values:
                # if value for variable is known, return it
                return var_values[x]
            elif x in replacements:
                # get replacement for variable
                (y, sgn) = replacements[x]
                # find details for replacing variable
                value = find_value(y, replacements, var_values)
                # construct, set, and return new value
                var_values[x] = value if sgn == 1 else 1 - value
                return var_values[x]
            else:
                raise QiskitOptimizationError('Invalid values!')

        # loop over all variables to set their values
        for x_i in problem_ref.variables:
            if x_i.name not in var_values:
                find_value(x_i.name, replacements, var_values)

        # construct result
        x = [var_values[x_aux.name] for x_aux in problem_ref.variables]
        fval = result.fval
        results = OptimizationResult(x, fval, (replacements, qubo_converter))
        results = qubo_converter.decode(results)
        return results