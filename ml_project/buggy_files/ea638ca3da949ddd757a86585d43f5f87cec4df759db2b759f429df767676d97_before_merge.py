def openid():

    oidc_configuration, jwt_key_set = get_oidc_configuration(current_app)
    token_endpoint = oidc_configuration['token_endpoint']
    userinfo_endpoint = oidc_configuration['userinfo_endpoint']

    data = {
        'grant_type': 'authorization_code',
        'code': request.json['code'],
        'redirect_uri': request.json['redirectUri'],
        'client_id': request.json['clientId'],
        'client_secret': current_app.config['OAUTH2_CLIENT_SECRET'],
    }
    r = requests.post(token_endpoint, data)
    token = r.json()

    if 'error' in token:
        error_text = token.get('error_description') or token['error']
        raise ApiError(error_text)

    try:
        if current_app.config['OIDC_VERIFY_TOKEN']:
            jwt_header = jwt.get_unverified_header(token['id_token'])
            public_key = jwt_key_set[jwt_header['kid']]

            id_token = jwt.decode(
                token['id_token'],
                key=public_key,
                algorithms=jwt_header['alg']
            )
        else:
            id_token = jwt.decode(
                token['id_token'],
                verify=False
            )
    except Exception:
        current_app.logger.warning('No ID token in OpenID Connect token response.')
        id_token = {}

    try:
        headers = {'Authorization': '{} {}'.format(token.get('token_type', 'Bearer'), token['access_token'])}
        r = requests.get(userinfo_endpoint, headers=headers)
        userinfo = r.json()
    except Exception:
        raise ApiError('No access token in OpenID Connect token response.')

    subject = userinfo['sub']
    name = userinfo.get('name') or id_token.get('name')
    username = userinfo.get('preferred_username') or id_token.get('preferred_username')
    nickname = userinfo.get('nickname') or id_token.get('nickname')
    email = userinfo.get('email') or id_token.get('email')
    email_verified = userinfo.get('email_verified', id_token.get('email_verified', bool(email)))
    email_verified = True if email_verified == 'true' else email_verified  # Cognito returns string boolean
    picture = userinfo.get('picture') or id_token.get('picture')

    role_claim = current_app.config['OIDC_ROLE_CLAIM']
    group_claim = current_app.config['OIDC_GROUP_CLAIM']
    custom_claims = {
        role_claim: userinfo.get(role_claim) or id_token.get(role_claim, []),
        group_claim: userinfo.get(group_claim) or id_token.get(group_claim, []),
    }

    login = username or nickname or email
    if not login:
        raise ApiError("Must support one of the following OpenID claims: 'preferred_username', 'nickname' or 'email'", 400)

    user = User.find_by_id(id=subject)
    if not user:
        user = User(id=subject, name=name, login=login, password='', email=email,
                    roles=current_app.config['USER_ROLES'], text='', email_verified=email_verified)
        user.create()
    else:
        user.update(login=login, email=email)

    roles = custom_claims[role_claim] + user.roles
    groups = custom_claims[group_claim]

    if user.status != 'active':
        raise ApiError('User {} is not active'.format(login), 403)

    if not_authorized('ALLOWED_OIDC_ROLES', roles) or not_authorized('ALLOWED_EMAIL_DOMAINS', groups=[user.domain]):
        raise ApiError('User {} is not authorized'.format(login), 403)
    user.update_last_login()

    scopes = Permission.lookup(login, roles=roles)
    customers = get_customers(login, groups=[user.domain] + groups)

    auth_audit_trail.send(current_app._get_current_object(), event='openid-login', message='user login via OpenID Connect',
                          user=login, customers=customers, scopes=scopes, **custom_claims,
                          resource_id=subject, type='user', request=request)

    token = create_token(user_id=subject, name=name, login=login, provider=current_app.config['AUTH_PROVIDER'],
                         customers=customers, scopes=scopes, **custom_claims,
                         email=email, email_verified=email_verified, picture=picture)
    return jsonify(token=token.tokenize)