def report_final_result(metric):
    """
    Reports final result to NNI.

    Parameters
    ----------
    metric:
        serializable object.
    """
    assert _params or trial_env_vars.NNI_PLATFORM is None, \
        'nni.get_next_parameter() needs to be called before report_final_result'
    metric = json_tricks.dumps({
        'parameter_id': _params['parameter_id'] if _params else None,
        'trial_job_id': trial_env_vars.NNI_TRIAL_JOB_ID,
        'type': 'FINAL',
        'sequence': 0,
        'value': metric
    })
    platform.send_metric(metric)