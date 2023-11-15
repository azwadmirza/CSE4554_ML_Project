def cc_search_topo(request, obj_id, category, biz_cc_id, supplier_account):
    """
    @summary: 查询对象拓扑
    @param request:
    @param biz_cc_id:
    @return:
    """
    client = get_client_by_request(request)
    kwargs = {
        'bk_biz_id': biz_cc_id,
        'bk_supplier_account': supplier_account
    }
    cc_result = client.cc.search_biz_inst_topo(kwargs)
    if not cc_result['result']:
        message = handle_api_error('cc', 'cc.search_biz_inst_topo', kwargs, cc_result['message'])
        logger.error(message)
        result = {
            'result': False,
            'data': [],
            'message': message
        }
        return JsonResponse(result)

    if category in ["normal", "prev", "picker"]:
        cc_topo = cc_format_topo_data(cc_result['data'], obj_id, category)
    else:
        cc_topo = []

    return JsonResponse({'result': True, 'data': cc_topo})