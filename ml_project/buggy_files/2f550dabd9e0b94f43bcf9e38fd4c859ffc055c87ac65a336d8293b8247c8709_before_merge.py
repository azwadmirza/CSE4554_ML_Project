    def __init__(self, iss: str, typ: str, sub: str, aud: str, exp: dt, nbf: dt, iat: dt, jti: str = None, **kwargs) -> None:

        self.issuer = iss
        self.type = typ
        self.subject = sub
        self.audience = aud
        self.expiration = exp
        self.not_before = nbf
        self.issued_at = iat
        self.jwt_id = jti

        self.name = kwargs.get('name')
        self.preferred_username = kwargs.get('preferred_username')
        self.email = kwargs.get('email')
        self.provider = kwargs.get('provider')
        self.orgs = kwargs.get('orgs', list())
        self.groups = kwargs.get('groups', list())
        self.roles = kwargs.get('roles', list())
        self.scopes = kwargs.get('scopes', list())
        self.email_verified = kwargs.get('email_verified')
        self.picture = kwargs.get('picture')
        self.customers = kwargs.get('customers')