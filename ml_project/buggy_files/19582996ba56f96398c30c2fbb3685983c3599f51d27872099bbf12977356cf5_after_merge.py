def cmdb_get_mainline_object_topo(request, bk_biz_id, bk_supplier_account=''):
    """
    @summary: 获取配置平台业务拓扑模型
    @param request:
    @param bk_biz_id:
    @param bk_supplier_account:
    @return:
    """
    kwargs = {
        'bk_biz_id': bk_biz_id,
        'bk_supplier_account': bk_supplier_account,
    }
    client = get_client_by_user(request.user.username)
    cc_result = client.cc.get_mainline_object_topo(kwargs)
    if not cc_result['result']:
        message = handle_api_error(_(u"配置平台(CMDB)"),
                                   'cc.get_mainline_object_topo',
                                   kwargs,
                                   cc_result['message'])
        return {'result': cc_result['result'], 'code': cc_result['code'], 'message': message}
    data = cc_result['data']
    for bk_obj in data:
        if bk_obj['bk_obj_id'] == 'host':
            bk_obj['bk_obj_name'] = 'IP'
    result = {'result': cc_result['result'], 'code': cc_result['code'], 'data': cc_result['data']}
    return JsonResponse(result)