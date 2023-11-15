def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            auth_header = request.headers['Authorization']
        except KeyError:
            return abort(403, 'API token not found in Authorization header.')

        if auth_header:
            split = auth_header.split(" ")
            if len(split) != 2 or split[0] != 'Token':
                abort(403, 'Malformed authorization header.')
            auth_token = split[1]
        else:
            auth_token = ''
        if not Journalist.validate_api_token_and_get_user(auth_token):
            return abort(403, 'API token is invalid or expired.')
        return f(*args, **kwargs)
    return decorated_function