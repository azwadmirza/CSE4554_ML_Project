def queries(query_group,
            query_file=None,
            verbose=False,
            report_version_with_day=True):
    '''
    Run the set of queries represented by ``query_group`` from the
    configuration in the file query_file

    query_group
        Group of queries to run

    query_file
        salt:// file which will be parsed for osquery queries

    verbose
        Defaults to False. If set to True, more information (such as the query
        which was run) will be included in the result.

    CLI Examples:

    .. code_block:: bash

        salt '*' nebula.queries day
        salt '*' nebula.queries hour verbose=True
        salt '*' nebula.queries hour pillar_key=sec_osqueries
    '''
    query_data = {}
    MAX_FILE_SIZE = 104857600
    if query_file is None:
        if salt.utils.is_windows():
            query_file = 'salt://hubblestack_nebula/hubblestack_nebula_win_queries.yaml'
        else:
            query_file = 'salt://hubblestack_nebula/hubblestack_nebula_queries.yaml'
    if not isinstance(query_file, list):
        query_file = [query_file]
    for fh in query_file:
        if 'salt://' in fh:
            orig_fh = fh
            fh = __salt__['cp.cache_file'](fh)
        if fh is None:
            log.error('Could not find file {0}.'.format(orig_fh))
            return None
        if os.path.isfile(fh):
            with open(fh, 'r') as f:
                f_data = yaml.safe_load(f)
                if not isinstance(f_data, dict):
                    raise CommandExecutionError('File data is not formed as a dict {0}'
                                                .format(f_data))
                query_data =  _dict_update(query_data,
                                           f_data,
                                           recursive_update=True,
                                           merge_lists=True)

    if 'osquerybinpath' not in __grains__:
        if query_group == 'day':
            log.warning('osquery not installed on this host. Returning baseline data')
            # Match the formatting of normal osquery results. Not super
            #   readable, but just add new dictionaries to the list as we need
            #   more data
            ret = []
            ret.append(
                    {'fallback_osfinger': {
                         'data': [{'osfinger': __grains__.get('osfinger', __grains__.get('osfullname')),
                                   'osrelease': __grains__.get('osrelease', __grains__.get('lsb_distrib_release'))}],
                         'result': True
                    }}
            )
            if 'pkg.list_pkgs' in __salt__:
                ret.append(
                        {'fallback_pkgs': {
                             'data': [{'name': k, 'version': v} for k, v in __salt__['pkg.list_pkgs']().iteritems()],
                             'result': True
                        }}
                )
            uptime = __salt__['status.uptime']()
            if isinstance(uptime, dict):
                uptime = uptime.get('seconds', __salt__['cmd.run']('uptime'))
            ret.append(
                    {'fallback_uptime': {
                         'data': [{'uptime': uptime}],
                         'result': True
                    }}
            )
            if report_version_with_day:
                ret.append(hubble_versions())
            return ret
        else:
            log.debug('osquery not installed on this host. Skipping.')
            return None

    if salt.utils.is_windows():
        win_version = __grains__['osfullname']
        if '2008' not in win_version and '2012' not in win_version and '2016' not in win_version:
            log.error('osquery does not run on windows versions earlier than Server 2008 and Windows 7')
            if query_group == 'day':
                ret = []
                ret.append(
                        {'fallback_osfinger': {
                             'data': [{'osfinger': __grains__.get('osfinger', __grains__.get('osfullname')),
                                       'osrelease': __grains__.get('osrelease', __grains__.get('lsb_distrib_release'))}],
                             'result': True
                        }}
                )
                ret.append(
                        {'fallback_error': {
                             'data': 'osqueryi is installed but not compatible with this version of windows',
                             'result': True
                        }}
                )
                return ret
            else:
               return None

    query_data = query_data.get(query_group, [])

    if not query_data:
        return None

    ret = []
    for query in query_data:
        name = query.get('query_name')
        query_sql = query.get('query')
        if not query_sql:
            continue

        # Run the osqueryi query
        query_ret = {
            'result': True,
        }

        cmd = [__grains__['osquerybinpath'], '--read_max', MAX_FILE_SIZE, '--json', query_sql]
        res = __salt__['cmd.run_all'](cmd)
        if res['retcode'] == 0:
            query_ret['data'] = json.loads(res['stdout'])
        else:
            query_ret['result'] = False
            query_ret['error'] = res['stderr']

        if verbose:
            tmp = copy.deepcopy(query)
            tmp['query_result'] = query_ret
            ret.append(tmp)
        else:
            ret.append({name: query_ret})

    if query_group == 'day' and report_version_with_day:
        ret.append(hubble_versions())

    for r in ret:
        for query_name, query_ret in r.iteritems():
            for result in query_ret['data']:
                for key, value in result.iteritems():
                    if value and isinstance(value, basestring) and value.startswith('__JSONIFY__'):
                        result[key] = json.loads(value[len('__JSONIFY__'):])

    return ret