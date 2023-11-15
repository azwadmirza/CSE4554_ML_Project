def check_pipeline_job_runtime_conf(runtime_conf: typing.Dict):
    detect_utils.check_config(runtime_conf, ['initiator', 'job_parameters', 'role'])
    detect_utils.check_config(runtime_conf['initiator'], ['role', 'party_id'])
    detect_utils.check_config(runtime_conf['job_parameters'], [('work_mode', RuntimeConfig.WORK_MODE)])
    # deal party id
    runtime_conf['initiator']['party_id'] = int(runtime_conf['initiator']['party_id'])
    for r in runtime_conf['role'].keys():
        for i in range(len(runtime_conf['role'][r])):
            runtime_conf['role'][r][i] = int(runtime_conf['role'][r][i])