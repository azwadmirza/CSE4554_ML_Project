def report_intermediate_result(metric):
    """
    Reports intermediate result to NNI.

    Parameters
    ----------
    metric:
        serializable object.
    """
    global _intermediate_seq
    assert _params or trial_env_vars.NNI_PLATFORM is None, \
        'nni.get_next_parameter() needs to be called before report_intermediate_result'
    metric = json_tricks.dumps({
        'parameter_id': _params['parameter_id'] if _params else None,
        'trial_job_id': trial_env_vars.NNI_TRIAL_JOB_ID,
        'type': 'PERIODICAL',
        'sequence': _intermediate_seq,
        'value': metric
    })
    _intermediate_seq += 1
    platform.send_metric(metric)