    def parse(cls, token: str, key: str = None, verify: bool = True, algorithm: str = 'HS256') -> 'Jwt':
        try:
            json = jwt.decode(
                token,
                key=key or current_app.config['SECRET_KEY'],
                verify=verify,
                algorithms=algorithm,
                audience=current_app.config['OAUTH2_CLIENT_ID'] or current_app.config['SAML2_ENTITY_ID'] or absolute_url()
            )
        except (DecodeError, ExpiredSignature, InvalidAudience):
            raise

        return Jwt(
            iss=json.get('iss', None),
            typ=json.get('typ', None),
            sub=json.get('sub', None),
            aud=json.get('aud', None),
            exp=json.get('exp', None),
            nbf=json.get('nbf', None),
            iat=json.get('iat', None),
            jti=json.get('jti', None),
            name=json.get('name', None),
            preferred_username=json.get('preferred_username', None),
            email=json.get('email', None),
            provider=json.get('provider', None),
            orgs=json.get('orgs', list()),
            groups=json.get('groups', list()),
            roles=json.get('roles', list()),
            scopes=json.get('scope', '').split(' '),  # eg. scope='read write' => scopes=['read', 'write']
            email_verified=json.get('email_verified', None),
            picture=json.get('picture', None),
            customers=[json['customer']] if 'customer' in json else json.get('customers', list())
        )