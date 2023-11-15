def _check_cublas_info_array_if_synchronization_allowed(routine, info_array):
    # `info_array` contains integers, the status codes of a cuBLAS routine
    # call. It is referrd to as "infoArray" or "devInfoArray" in the official
    # cuBLAS documentation.
    assert isinstance(info_array, core.ndarray)
    assert info_array.ndim == 1

    config_linalg = cupyx._ufunc_config.get_config_linalg()
    # Only 'ignore' and 'raise' are currently supported.
    if config_linalg == 'ignore':
        return

    assert config_linalg == 'raise'
    if (info_array != 0).any():
        raise linalg.LinAlgError(
            'Error reported by {} in cuBLAS. infoArray/devInfoArray = {}.'
            ' Please refer to the cuBLAS documentation.'.format(
                routine.__name__, info_array))