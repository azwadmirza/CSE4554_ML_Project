def _blas_info():
    config = np.__config__
    blas_info = config.blas_opt_info
    blas = None
    if hasattr(config,'mkl_info') or any('mkl' in lib for lib in blas_info['libraries']):
        blas = 'INTEL MKL'
    elif hasattr(config,'openblas_info') or any('openblas' in lib for lib in blas_info['libraries']):
        blas = 'OPENBLAS'
    elif 'extra_link_args' in blas_info.keys() and ('-Wl,Accelerate' in blas_info['extra_link_args']):
        blas = 'Accelerate'
    else:
        blas = 'Generic'
    return blas