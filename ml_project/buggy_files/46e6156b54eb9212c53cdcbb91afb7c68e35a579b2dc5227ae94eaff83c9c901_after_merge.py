def job_get_script_list(request, biz_cc_id):
    """
    查询业务脚本列表
    :param request:
    :param biz_cc_id:
    :return:
    """
    # 查询脚本列表
    client = get_client_by_user(request.user.username)
    script_type = request.GET.get('type')
    kwargs = {
        'bk_biz_id': biz_cc_id,
        'is_public': True if script_type == 'public' else False
    }
    script_result = client.job.get_script_list(kwargs)

    if not script_result['result']:
        message = handle_api_error('cc', 'job.get_script_list', kwargs, script_result['message'])
        logger.error(message)
        result = {
            'result': False,
            'message': message
        }
        return JsonResponse(result)

    script_dict = {}
    for script in script_result['data']['data']:
        script_dict.setdefault(script['name'], []).append(script['id'])

    version_data = []
    for name, version in script_dict.items():
        version_data.append({
            "text": name,
            "value": max(version)
        })

    return JsonResponse({'result': True, 'data': version_data})