def cc_search_object_attribute(request, obj_id, biz_cc_id, supplier_account):
    """
    @summary: 获取对象自定义属性
    @param request:
    @param biz_cc_id:
    @return:
    """
    client = get_client_by_request(request)
    kwargs = {
        'bk_obj_id': obj_id,
        'bk_supplier_account': supplier_account
    }
    cc_result = client.cc.search_object_attribute(kwargs)
    if not cc_result['result']:
        message = handle_api_error('cc', 'cc.search_object_attribute', kwargs, cc_result['message'])
        logger.error(message)
        result = {
            'result': False,
            'data': [],
            'message': message
        }
        return JsonResponse(result)

    obj_property = []
    for item in cc_result['data']:
        if item['editable']:
            obj_property.append({
                'value': item['bk_property_id'],
                'text': item['bk_property_name']
            })

    return JsonResponse({'result': True, 'data': obj_property})