    def optimize(self, num_vars, objective_function, gradient_function=None,
                 variable_bounds=None, initial_point=None):
        num_procs = multiprocessing.cpu_count() - 1
        num_procs = \
            num_procs if self._max_processes is None else min(num_procs, self._max_processes)
        num_procs = num_procs if num_procs >= 0 else 0

        if platform.system() == 'Darwin':
            # Changed in version 3.8: On macOS, the spawn start method is now the
            # default. The fork start method should be considered unsafe as it can
            # lead to crashes.
            # However P_BFGS doesn't support spawn, so we revert to single process.
            major, minor, _ = platform.python_version_tuple()
            if major > '3' or (major == '3' and minor >= '8'):
                num_procs = 0
                logger.warning("For MacOS, python >= 3.8, using only current process. "
                               "Multiple core use not supported.")
        elif platform.system() == 'Windows':
            num_procs = 0
            logger.warning("For Windows, using only current process. "
                           "Multiple core use not supported.")

        queue = multiprocessing.Queue()
        # bounds for additional initial points in case bounds has any None values
        threshold = 2 * np.pi
        if variable_bounds is None:
            variable_bounds = [(-threshold, threshold)] * num_vars
        low = [(l if l is not None else -threshold) for (l, u) in variable_bounds]
        high = [(u if u is not None else threshold) for (l, u) in variable_bounds]

        def optimize_runner(_queue, _i_pt):  # Multi-process sampling
            _sol, _opt, _nfev = self._optimize(num_vars, objective_function,
                                               gradient_function, variable_bounds, _i_pt)
            _queue.put((_sol, _opt, _nfev))

        # Start off as many other processes running the optimize (can be 0)
        processes = []
        for _ in range(num_procs):
            i_pt = aqua_globals.random.uniform(low, high)  # Another random point in bounds
            p = multiprocessing.Process(target=optimize_runner, args=(queue, i_pt))
            processes.append(p)
            p.start()

        # While the one _optimize in this process below runs the other processes will
        # be running to. This one runs
        # with the supplied initial point. The process ones have their own random one
        sol, opt, nfev = self._optimize(num_vars, objective_function,
                                        gradient_function, variable_bounds, initial_point)

        for p in processes:
            # For each other process we wait now for it to finish and see if it has
            # a better result than above
            p.join()
            p_sol, p_opt, p_nfev = queue.get()
            if p_opt < opt:
                sol, opt = p_sol, p_opt
            nfev += p_nfev

        return sol, opt, nfev