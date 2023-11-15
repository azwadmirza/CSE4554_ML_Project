def _check_cusolver_dev_info_if_synchronization_allowed(routine, dev_info):
    # `dev_info` contains a single integer, the status code of a cuSOLVER
    # routine call. It is referred to as "devInfo" in the official cuSOLVER
    # documentation.
    assert isinstance(dev_info, core.ndarray)
    assert dev_info.size == 1
    config_linalg = cupyx._ufunc_config.get_config_linalg()
    # Only 'ignore' and 'raise' are currently supported.
    if config_linalg == 'ignore':
        return

    assert config_linalg == 'raise'
    dev_info_host = dev_info.item()
    if dev_info_host != 0:
        raise linalg.LinAlgError(
            'Error reported by {} in cuSOLVER. devInfo = {}. Please refer'
            ' to the cuSOLVER documentation.'.format(
                routine.__name__, dev_info_host))