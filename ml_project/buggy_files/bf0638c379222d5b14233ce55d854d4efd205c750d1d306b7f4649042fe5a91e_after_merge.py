    def post(self):  # pylint: disable=arguments-differ
        """
        :ref:`Authenticate <rest_tornado-auth>` against Salt's eauth system

        .. http:post:: /login

            :reqheader X-Auth-Token: |req_token|
            :reqheader Accept: |req_accept|
            :reqheader Content-Type: |req_ct|

            :form eauth: the eauth backend configured for the user
            :form username: username
            :form password: password

            :status 200: |200|
            :status 400: |400|
            :status 401: |401|
            :status 406: |406|
            :status 500: |500|

        **Example request:**

        .. code-block:: bash

            curl -si localhost:8000/login \\
                    -H "Accept: application/json" \\
                    -d username='saltuser' \\
                    -d password='saltpass' \\
                    -d eauth='pam'

        .. code-block:: text

            POST / HTTP/1.1
            Host: localhost:8000
            Content-Length: 42
            Content-Type: application/x-www-form-urlencoded
            Accept: application/json

            username=saltuser&password=saltpass&eauth=pam

        **Example response:**

        .. code-block:: text

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
        """
        try:
            if not isinstance(self.request_payload, dict):
                self.send_error(400)
                return

            creds = {
                "username": self.request_payload["username"],
                "password": self.request_payload["password"],
                "eauth": self.request_payload["eauth"],
            }
        # if any of the args are missing, its a bad request
        except KeyError:
            self.send_error(400)
            return

        token = self.application.auth.mk_token(creds)
        if "token" not in token:
            # TODO: nicer error message
            # 'Could not authenticate using provided credentials')
            self.send_error(401)
            # return since we don't want to execute any more
            return
        self.set_cookie(AUTH_COOKIE_NAME, token["token"])

        # Grab eauth config for the current backend for the current user
        try:
            eauth = self.application.opts["external_auth"][token["eauth"]]
            # Get sum of '*' perms, user-specific perms, and group-specific perms
            perms = eauth.get(token["name"], [])
            perms.extend(eauth.get("*", []))

            if "groups" in token and token["groups"]:
                user_groups = set(token["groups"])
                eauth_groups = {i.rstrip("%") for i in eauth.keys() if i.endswith("%")}

                for group in user_groups & eauth_groups:
                    perms.extend(eauth["{}%".format(group)])

            perms = sorted(list(set(perms)))
        # If we can't find the creds, then they aren't authorized
        except KeyError:
            self.send_error(401)
            return

        except (AttributeError, IndexError):
            log.debug(
                "Configuration for external_auth malformed for eauth '%s', "
                "and user '%s'.",
                token.get("eauth"),
                token.get("name"),
                exc_info=True,
            )
            # TODO better error -- 'Configuration for external_auth could not be read.'
            self.send_error(500)
            return

        ret = {
            "return": [
                {
                    "token": token["token"],
                    "expire": token["expire"],
                    "start": token["start"],
                    "user": token["name"],
                    "eauth": token["eauth"],
                    "perms": perms,
                }
            ]
        }

        self.write(self.serialize(ret))