def _default_steadystate_args():
    def_args = {'sparse': True, 'use_rcm': False,
                'use_wbm': False, 'weight': None, 'use_precond': False,
                'all_states': False, 'M': None, 'x0': None, 'drop_tol': 1e-4,
                'fill_factor': 100, 'diag_pivot_thresh': None, 'maxiter': 1000,
                'tol': 1e-12, 'matol': 1e-15, 'mtol': None,
                'permc_spec': 'COLAMD', 'ILU_MILU': 'smilu_2',
                'restart': 20, 'return_info': False,
                'info': _empty_info_dict(),
                'verbose': False, 'solver': 'scipy'}

    return def_args