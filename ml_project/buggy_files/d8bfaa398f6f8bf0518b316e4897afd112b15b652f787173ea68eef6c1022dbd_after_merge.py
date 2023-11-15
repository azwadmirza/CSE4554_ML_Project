    def __init__(self, secret, cookie_name='auth_tkt', secure=False,
                 include_ip=False, timeout=None, reissue_time=None,
                 max_age=None, http_only=False, path="/", wild_domain=True,
                 hashalg='md5', parent_domain=False, domain=None):

        serializer = SimpleSerializer()

        self.cookie_profile = CookieProfile(
            cookie_name=cookie_name,
            secure=secure,
            max_age=max_age,
            httponly=http_only,
            path=path,
            serializer=serializer
        )

        self.secret = secret
        self.cookie_name = cookie_name
        self.secure = secure
        self.include_ip = include_ip
        self.timeout = timeout if timeout is None else int(timeout)
        self.reissue_time = reissue_time if reissue_time is None else int(reissue_time)
        self.max_age = max_age if max_age is None else int(max_age)
        self.wild_domain = wild_domain
        self.parent_domain = parent_domain
        self.domain = domain
        self.hashalg = hashalg