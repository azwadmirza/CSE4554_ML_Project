def init_job_queue():
    if WORK_MODE == WorkMode.STANDALONE:
        job_queue = InProcessQueue()
        RuntimeConfig.init_config(JOB_QUEUE=job_queue)
    elif WORK_MODE == WorkMode.CLUSTER:
        job_queue = RedisQueue(queue_name='fate_flow_job_queue', host=REDIS['host'], port=REDIS['port'],
                               password=REDIS['password'], max_connections=REDIS['max_connections'])
        RuntimeConfig.init_config(JOB_QUEUE=job_queue)
    else:
        raise Exception('init queue failed.')