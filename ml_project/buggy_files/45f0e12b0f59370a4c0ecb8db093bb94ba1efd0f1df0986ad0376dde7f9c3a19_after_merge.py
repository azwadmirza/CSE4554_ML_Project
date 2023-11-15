def returner(ret):
    '''
    Process the return from Salt
    '''
    job_fun = ret['fun']
    job_fun_escaped = job_fun.replace('.', '_')
    job_id = ret['jid']
    job_minion_id = ret['id']
    job_success = True if ret['return'] else False
    job_retcode = ret.get('retcode', 1)

    index = 'salt-{0}'.format(job_fun_escaped)
    if __salt__['config.option']('elasticsearch:index_date', False):
        index = '{0}-{1}'.format(index,
            datetime.date.today().strftime('%Y.%m.%d'))
    functions_blacklist = __salt__['config.option'](
        'elasticsearch:functions_blacklist', [])
    doc_type_version = __salt__['config.option'](
        'elasticsearch:doc_type', 'default')

    if job_fun in functions_blacklist:
        log.info(
            'Won\'t push new data to Elasticsearch, job with jid={0} and '
            'function={1} which is in the user-defined list of ignored '
            'functions'.format(job_id, job_fun))
        return

    if not job_success:
        log.info('Won\'t push new data to Elasticsearch, job with jid={0} was '
                 'not succesful'.format(job_id))
        return

    _ensure_index(index)

    class UTC(tzinfo):
        def utcoffset(self, dt):
            return timedelta(0)

        def tzname(self, dt):
            return 'UTC'

        def dst(self, dt):
            return timedelta(0)

    if isinstance(ret['return'], dict):
        sk = ""
        for k in ret['return'].keys():
            sk = k.replace('.', '_')
            ret['return'][sk] = ret['return'].pop(k)

    utc = UTC()
    data = {
        '@timestamp': datetime.now(utc).isoformat(),
        'success': job_success,
        'retcode': job_retcode,
        'minion': job_minion_id,
        'fun': job_fun,
        'jid': job_id,
        'data': ret['return'],
    }

    ret = __salt__['elasticsearch.document_create'](index=index,
                                                    doc_type=doc_type_version,
                                                    body=json.dumps(data))