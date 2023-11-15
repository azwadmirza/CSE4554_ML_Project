def redirect_uri(provider):
    if provider == 'facebook':
        provider_class = FbOAuth()
    elif provider == 'google':
        provider_class = GoogleOAuth()
    elif provider == 'twitter':
        provider_class = TwitterOAuth()
    elif provider == 'instagram':
        provider_class = InstagramOAuth()
    else:
        return make_response(jsonify(
            message="No support for {}".format(provider)), 404)
    url = provider_class.get_auth_uri() + '?client_id=' +\
        provider_class.get_client_id() + '&redirect_uri=' +\
        provider_class.get_redirect_uri()
    return make_response(jsonify(url=url), 200)