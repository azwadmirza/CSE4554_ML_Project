    def __init__(self, cookie_name='csrf_token', secure=False, httponly=False,
                 domain=None, max_age=None, path='/'):
        serializer = SimpleSerializer()
        self.cookie_profile = CookieProfile(
            cookie_name=cookie_name,
            secure=secure,
            max_age=max_age,
            httponly=httponly,
            path=path,
            domains=[domain],
            serializer=serializer
        )
        self.cookie_name = cookie_name