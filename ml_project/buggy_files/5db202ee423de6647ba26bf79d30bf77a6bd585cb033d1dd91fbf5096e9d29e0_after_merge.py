def _get_business_info(request, app_id, use_cache=True, use_maintainer=False):
    """Get detail infomations for a exact app_id.

    @param object request: django request object.
    @param int app_id: cc_id of core.business model.
    @param use_maintainer: 使用运维身份请求
    """
    username = request.user.username
    business = Business.objects.get(cc_id=app_id)
    cache_key = "%s_get_business_info_%s_%s" % (CACHE_PREFIX, app_id, username)
    data = cache.get(cache_key)

    if not (use_cache and data):
        if use_maintainer:
            client = get_client_by_user_and_biz_id(username, app_id)
        else:
            client = get_client_by_user(request.user.username)
        result = client.cc.search_business({
            'bk_supplier_account': business.cc_owner,
            'condition': {
                'bk_biz_id': int(app_id)
            }
        })

        if result['result']:
            if not result['data']['info']:
                raise exceptions.Forbidden()
            data = result['data']['info'][0]
        elif result.get('code') in ('20101', 20101):
            raise exceptions.Unauthorized(result['message'])
        elif result.get('code') in ('20103', 20103, '20201', 20201,
                                    '20202', 20202):
            raise exceptions.Forbidden(result['message'])
        else:
            raise exceptions.APIError(
                'cc',
                'get_app_by_id',
                result.get('detail_message', result['message'])
            )

        cache.set(cache_key, data, DEFAULT_CACHE_TIME_FOR_CC)

    return data