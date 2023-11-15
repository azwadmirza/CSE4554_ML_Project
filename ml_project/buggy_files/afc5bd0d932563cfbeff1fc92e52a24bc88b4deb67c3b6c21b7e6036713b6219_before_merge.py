    def POST(self, **kwargs):
        '''
        :ref:`Authenticate  <rest_cherrypy-auth>` against Salt's eauth system

        .. http:post:: /login

            :reqheader X-Auth-Token: |req_token|
            :reqheader Accept: |req_accept|
            :reqheader Content-Type: |req_ct|

            :form eauth: the eauth backend configured for the user
            :form username: username
            :form password: password

            :status 200: |200|
            :status 401: |401|
            :status 406: |406|

        **Example request:**

        .. code-block:: bash

            curl -si localhost:8000/login \\
                    -H "Accept: application/json" \\
                    -d username='saltuser' \\
                    -d password='saltpass' \\
                    -d eauth='pam'

        .. code-block:: http

            POST / HTTP/1.1
            Host: localhost:8000
            Content-Length: 42
            Content-Type: application/x-www-form-urlencoded
            Accept: application/json

            username=saltuser&password=saltpass&eauth=pam

        **Example response:**

        .. code-block:: http

            HTTP/1.1 200 OK
            Content-Type: application/json
            Content-Length: 206
            X-Auth-Token: 6d1b722e
            Set-Cookie: session_id=6d1b722e; expires=Sat, 17 Nov 2012 03:23:52 GMT; Path=/

            {"return": {
                "token": "6d1b722e",
                "start": 1363805943.776223,
                "expire": 1363849143.776224,
                "user": "saltuser",
                "eauth": "pam",
                "perms": [
                    "grains.*",
                    "status.*",
                    "sys.*",
                    "test.*"
                ]
            }}
        '''
        if not self.api._is_master_running():
            raise salt.exceptions.SaltDaemonNotRunning(
                'Salt Master is not available.')

        # the urlencoded_processor will wrap this in a list
        if isinstance(cherrypy.serving.request.lowstate, list):
            creds = cherrypy.serving.request.lowstate[0]
        else:
            creds = cherrypy.serving.request.lowstate

        username = creds.get('username', None)
        # Validate against the whitelist.
        if not salt_api_acl_tool(username, cherrypy.request):
            raise cherrypy.HTTPError(401)

        # Mint token.
        token = self.auth.mk_token(creds)
        if 'token' not in token:
            raise cherrypy.HTTPError(401,
                    'Could not authenticate using provided credentials')

        cherrypy.response.headers['X-Auth-Token'] = cherrypy.session.id
        cherrypy.session['token'] = token['token']
        cherrypy.session['timeout'] = (token['expire'] - token['start']) / 60

        # Grab eauth config for the current backend for the current user
        try:
            eauth = self.opts.get('external_auth', {}).get(token['eauth'], {})

            # Get sum of '*' perms, user-specific perms, and group-specific perms
            perms = eauth.get(token['name'], [])
            perms.extend(eauth.get('*', []))

            if 'groups' in token:
                user_groups = set(token['groups'])
                eauth_groups = set([i.rstrip('%') for i in eauth.keys() if i.endswith('%')])

                for group in user_groups & eauth_groups:
                    perms.extend(eauth['{0}%'.format(group)])

            if not perms:
                raise ValueError("Eauth permission list not found.")
        except (AttributeError, IndexError, KeyError, ValueError):
            logger.debug("Configuration for external_auth malformed for "
                "eauth '{0}', and user '{1}'."
                .format(token.get('eauth'), token.get('name')), exc_info=True)
            raise cherrypy.HTTPError(500,
                'Configuration for external_auth could not be read.')

        return {'return': [{
            'token': cherrypy.session.id,
            'expire': token['expire'],
            'start': token['start'],
            'user': token['name'],
            'eauth': token['eauth'],
            'perms': perms,
        }]}