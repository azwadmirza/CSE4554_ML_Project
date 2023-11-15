def _mkl_steadystate_args():
    def_args = {'max_iter_refine': 10,
                'scaling_vectors': True,
                'weighted_matching': True,
                'return_info': False, 'info': _empty_info_dict(), 
                'verbose': False, 'solver': 'mkl',
                'use_rcm': False,
                'use_wbm': False, 'weight': None,
                'tol': 1e-12,
                'maxiter': 1000}

    return def_args