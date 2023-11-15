    def tell_sentry(exception, state, allow_reraise=True):

        if isinstance(exception, pando.Response) and exception.code < 500:
            # Only log server errors
            return

        if isinstance(exception, NeedDatabase):
            # Don't flood Sentry when DB is down
            return

        if isinstance(exception, psycopg2.Error):
            from liberapay.website import website
            if getattr(website, 'db', None):
                try:
                    website.db.one('SELECT 1 AS x')
                except psycopg2.Error as e:
                    # If it can't answer this simple query, then it's either
                    # down or unreachable. Show the proper 503 error page.
                    website.db.okay = False
                    state['exception'] = NeedDatabase()
                    if sentry:
                        # Record the exception raised above instead of the
                        # original one, to avoid duplicate issues.
                        return tell_sentry(e, state, allow_reraise=True)

                if 'read-only' in str(exception):
                    # DB is in read only mode
                    state['db_is_readonly'] = True
                    # Show the proper 503 error page
                    state['exception'] = NeedDatabase()
                    # Don't reraise this in tests
                    allow_reraise = False

        if isinstance(exception, ValueError):
            if 'cannot contain NUL (0x00) characters' in str(exception):
                # https://github.com/liberapay/liberapay.com/issues/675
                response = state.get('response') or pando.Response()
                response.code = 400
                response.body = str(exception)
                return {'exception': None}

        if not sentry:
            # No Sentry, log to stderr instead
            traceback.print_exc()
            # Reraise if allowed
            if env.sentry_reraise and allow_reraise:
                raise
            return {'sentry_ident': None}

        # Prepare context data
        sentry_data = {}
        if state:
            try:
                sentry_data['tags'] = {
                    'lang': getattr(state.get('locale'), 'language', None),
                }
                request = state.get('request')
                user_data = sentry_data['user'] = {}
                if request is not None:
                    user_data['ip_address'] = str(request.source)
                    decode = lambda b: b.decode('ascii', 'backslashreplace')
                    sentry_data['request'] = {
                        'method': request.method,
                        'url': request.line.uri.decoded,
                        'headers': {
                            decode(k): decode(b', '.join(v))
                            for k, v in request.headers.items()
                            if k != b'Cookie'
                        },
                    }
                user = state.get('user')
                if isinstance(user, Participant):
                    user_data['id'] = getattr(user, 'id', None)
                    user_data['username'] = getattr(user, 'username', None)
            except Exception as e:
                tell_sentry(e, {})

        # Tell Sentry
        result = sentry.captureException(data=sentry_data)

        # Put the Sentry id in the state for logging, etc
        return {'sentry_ident': sentry.get_ident(result)}