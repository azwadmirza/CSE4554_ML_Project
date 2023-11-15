def cmdb_search_host(request, bk_biz_id, bk_supplier_account='', bk_supplier_id=0):
    """
    @summary: 获取 CMDB 上业务的 IP 列表，以及 agent 状态等信息
    @param request:
    @param bk_biz_id: 业务 CMDB ID
    @param bk_supplier_account: 业务开发商账号
    @param bk_supplier_id: 业务开发商ID
    @params fields: list 查询字段，默认只返回 bk_host_innerip、bk_host_name、bk_host_id, 可以查询主机的任意字段，也可以查询
                set、module、cloud、agent等信息
    @return:
    """
    fields = json.loads(request.GET.get('fields', '[]'))
    client = get_client_by_request(request)
    condition = [{
        'bk_obj_id': 'host',
        'fields': [],
    }]
    if 'set' in fields:
        condition.append({
            'bk_obj_id': 'set',
            'fields': [],
        })
    if 'module' in fields:
        condition.append({
            'bk_obj_id': 'module',
            'fields': [],
        })
    kwargs = {
        'bk_biz_id': bk_biz_id,
        'bk_supplier_account': bk_supplier_account,
        'condition': condition
    }
    host_result = client.cc.search_host(kwargs)
    if not host_result['result']:
        message = handle_api_error(_(u"配置平台(CMDB)"), 'cc.search_host', kwargs, host_result['message'])
        result = {'result': False, 'code': ERROR_CODES.API_CMDB_ERROR, 'message': message}
        return JsonResponse(result)

    host_info = host_result['data']['info']
    data = []
    default_fields = ['bk_host_innerip', 'bk_host_name', 'bk_host_id']
    fields = list(set(default_fields + fields))
    for host in host_info:
        host_detail = {field: host['host'][field] for field in fields if field in host['host']}
        if 'set' in fields:
            host_detail['set'] = host['set']
        if 'module' in fields:
            host_detail['module'] = host['module']
        if 'cloud' in fields or 'agent' in fields:
            host_detail['cloud'] = host['host']['bk_cloud_id']
        data.append(host_detail)

    if 'agent' in fields:
        agent_kwargs = {
            'bk_biz_id': bk_biz_id,
            'bk_supplier_id': bk_supplier_id,
            'hosts': [{'bk_cloud_id': host['cloud'][0]['id'], 'ip': host['bk_host_innerip']} for host in data]
        }
        agent_result = client.gse.get_agent_status(agent_kwargs)
        if not agent_result['result']:
            message = handle_api_error(_(u"管控平台(GSE)"),
                                       'gse.get_agent_status',
                                       agent_kwargs,
                                       agent_result['message'])
            result = {'result': False, 'code': ERROR_CODES.API_GSE_ERROR, 'message': message}
            return JsonResponse(result)

        agent_data = agent_result['data']
        for host in data:
            # agent在线状态，0为不在线，1为在线，-1为未知
            agent_info = agent_data.get('%s:%s' % (host['cloud'][0]['id'], host['bk_host_innerip']), {})
            host['agent'] = agent_info.get('bk_agent_alive', -1)

    result = {'result': True, 'code': NO_ERROR, 'data': data}
    return JsonResponse(result)