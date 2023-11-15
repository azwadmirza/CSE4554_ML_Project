def cc_search_create_object_attribute(request, obj_id, biz_cc_id, supplier_account):
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
            prop_dict = {
                'tag_code': item['bk_property_id'],
                'type': "input",
                'attrs': {
                    'name': item['bk_property_name'],
                    'editable': 'true',
                },
            }
            if item['bk_property_id'] in ['bk_set_name']:
                prop_dict["attrs"]["validation"] = [
                    {
                        "type": "required"
                    }
                ]
            obj_property.append(prop_dict)

    return JsonResponse({'result': True, 'data': obj_property})