def request_next_parameter():
    metric = to_json({
        'trial_job_id': trial_env_vars.NNI_TRIAL_JOB_ID,
        'type': 'REQUEST_PARAMETER',
        'sequence': 0,
        'parameter_index': _param_index
    })
    send_metric(metric)