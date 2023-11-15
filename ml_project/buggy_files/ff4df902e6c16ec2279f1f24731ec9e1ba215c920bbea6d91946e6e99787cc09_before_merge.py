def _get_user_business_list(request, use_cache=True):
    """Get authorized business list for a exact username.

    :param object request: django request object.
    :param bool use_cache: (Optional)
    """
    user = request.user
    cache_key = "%s_get_user_business_list_%s" % (CACHE_PREFIX, user.username)
    data = cache.get(cache_key)

    if not (use_cache and data):
        user_info = _get_user_info(request)
        client = get_client_by_request(request)
        result = client.cc.search_business({
            'bk_supplier_account': user_info['bk_supplier_account'],
            'condition': {
                'bk_data_status': {'$in': ['enable', 'disabled', None]},
                '$or': [{'bk_biz_developer': {"$regex": user.username}},
                        {'bk_biz_productor': {"$regex": user.username}},
                        {'bk_biz_maintainer': {"$regex": user.username}},
                        {'bk_biz_tester': {"$regex": user.username}}]
            }
        })

        if result['result']:
            data = result['data']['info']
            cache.set(cache_key, data, DEFAULT_CACHE_TIME_FOR_CC)
        elif result.get('code') in ('20101', 20101):
            raise exceptions.Unauthorized(result['message'])
        elif result.get('code') in ('20103', 20103, '20201', 20201,
                                    '20202', 20202):
            raise exceptions.Forbidden(result['message'])
        else:
            raise exceptions.APIError(
                'cc',
                'search_business',
                result.get('detail_message', result['message'])
            )

    return data