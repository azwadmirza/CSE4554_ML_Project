    def solve(self, problem: QuadraticProgram) -> MinimumEigenOptimizerResult:
        """Tries to solves the given problem using the optimizer.

        Runs the optimizer to try to solve the optimization problem.

        Args:
            problem: The problem to be solved.

        Returns:
            The result of the optimizer applied to the problem.

        Raises:
            QiskitOptimizationError: If problem not compatible.
        """
        # check compatibility and raise exception if incompatible
        msg = self.get_compatibility_msg(problem)
        if len(msg) > 0:
            raise QiskitOptimizationError('Incompatible problem: {}'.format(msg))

        # convert problem to QUBO
        qubo_converter = QuadraticProgramToQubo()
        problem_ = qubo_converter.encode(problem)

        # construct operator and offset
        operator_converter = QuadraticProgramToIsing()
        operator, offset = operator_converter.encode(problem_)

        # only try to solve non-empty Ising Hamiltonians
        if operator.num_qubits > 0:

            # approximate ground state of operator using min eigen solver
            eigen_results = self._min_eigen_solver.compute_minimum_eigenvalue(operator)

            # analyze results
            samples = eigenvector_to_solutions(eigen_results.eigenstate, operator)
            samples = [(res[0], problem_.objective.sense.value * (res[1] + offset), res[2])
                       for res in samples]
            samples.sort(key=lambda x: problem_.objective.sense.value * x[1])
            x = samples[0][0]
            fval = samples[0][1]

        # if Hamiltonian is empty, then the objective function is constant to the offset
        else:
            x = [0]*problem_.get_num_binary_vars()
            fval = offset
            x_str = '0'*problem_.get_num_binary_vars()
            samples = [(x_str, offset, 1.0)]

        # translate result back to integers
        opt_res = MinimumEigenOptimizerResult(x, fval, samples, qubo_converter)
        opt_res = qubo_converter.decode(opt_res)

        # translate results back to original problem
        return opt_res