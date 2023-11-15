def get_user_info(request):
    client = get_client_by_user(request.user.username)
    auth = getattr(client, settings.ESB_AUTH_COMPONENT_SYSTEM)
    _get_user_info = getattr(auth, settings.ESB_AUTH_GET_USER_INFO)
    user_info = _get_user_info({})
    if user_info['result']:
        user_info['data']['bk_supplier_account'] = 0
    return user_info