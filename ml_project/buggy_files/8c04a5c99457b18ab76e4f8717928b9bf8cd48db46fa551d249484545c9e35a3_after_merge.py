    def post(self):
        """
        .. http:post:: /certificates

           Creates a new certificate

           **Example request**:

           .. sourcecode:: http

              POST /certificates HTTP/1.1
              Host: example.com
              Accept: application/json, text/javascript

              {
                "country": "US",
                "state": "CA",
                "location": "A Place",
                "organization": "ExampleInc.",
                "organizationalUnit": "Operations",
                "owner": "bob@example.com",
                "description": "test",
                "selectedAuthority": "timetest2",
                "csr": "----BEGIN CERTIFICATE REQUEST-----...",
                "authority": {
                    "body": "-----BEGIN...",
                    "name": "timetest2",
                    "chain": "",
                    "notBefore": "2015-06-05T15:20:59",
                    "active": true,
                    "id": 50,
                    "notAfter": "2015-06-17T15:21:08",
                    "description": "dsfdsf"
                },
                "notifications": [
                    {
                      "description": "Default 30 day expiration notification",
                      "notificationOptions": [
                        {
                          "name": "interval",
                          "required": true,
                          "value": 30,
                          "helpMessage": "Number of days to be alert before expiration.",
                          "validation": "^\\d+$",
                          "type": "int"
                        },
                        {
                          "available": [
                            "days",
                            "weeks",
                            "months"
                          ],
                          "name": "unit",
                          "required": true,
                          "value": "days",
                          "helpMessage": "Interval unit",
                          "validation": "",
                          "type": "select"
                        },
                        {
                          "name": "recipients",
                          "required": true,
                          "value": "bob@example.com",
                          "helpMessage": "Comma delimited list of email addresses",
                          "validation": "^([\\w+-.%]+@[\\w-.]+\\.[A-Za-z]{2,4},?)+$",
                            "type": "str"
                          }
                        ],
                        "label": "DEFAULT_KGLISSON_30_DAY",
                        "pluginName": "email-notification",
                        "active": true,
                        "id": 7
                    }
                ],
                "extensions": {
                    "basicConstraints": {},
                    "keyUsage": {
                        "isCritical": true,
                        "useKeyEncipherment": true,
                        "useDigitalSignature": true
                    },
                    "extendedKeyUsage": {
                        "isCritical": true,
                        "useServerAuthentication": true
                    },
                    "subjectKeyIdentifier": {
                        "includeSKI": true
                    },
                    "subAltNames": {
                        "names": []
                    }
                },
                "commonName": "test",
                "validityStart": "2015-06-05T07:00:00.000Z",
                "validityEnd": "2015-06-16T07:00:00.000Z",
                "replacements": [
                    {'id': 123}
                ]
             }

           **Example response**:

           .. sourcecode:: http

              HTTP/1.1 200 OK
              Vary: Accept
              Content-Type: text/javascript

              {
                "id": 1,
                "name": "cert1",
                "description": "this is cert1",
                "bits": 2048,
                "deleted": false,
                "issuer": "ExampeInc.",
                "serial": "123450",
                "chain": "-----Begin ...",
                "body": "-----Begin ...",
                "san": true,
                "owner": "jimbob@example.com",
                "active": false,
                "notBefore": "2015-06-05T17:09:39",
                "notAfter": "2015-06-10T17:09:39",
                "cn": "example.com",
                "status": "unknown"
              }

           :arg extensions: extensions to be used in the certificate
           :arg description: description for new certificate
           :arg owner: owner email
           :arg validityStart: when the certificate should start being valid
           :arg validityEnd: when the certificate should expire
           :arg authority: authority that should issue the certificate
           :arg country: country for the CSR
           :arg state: state for the CSR
           :arg location: location for the CSR
           :arg organization: organization for CSR
           :arg commonName: certiifcate common name
           :reqheader Authorization: OAuth token to authenticate
           :statuscode 200: no error
           :statuscode 403: unauthenticated
        """
        self.reqparse.add_argument('extensions', type=dict, location='json')
        self.reqparse.add_argument('destinations', type=list, default=[], location='json')
        self.reqparse.add_argument('notifications', type=list, default=[], location='json')
        self.reqparse.add_argument('replacements', type=list, default=[], location='json')
        self.reqparse.add_argument('validityStart', type=str, location='json')  # TODO validate
        self.reqparse.add_argument('validityEnd', type=str, location='json')  # TODO validate
        self.reqparse.add_argument('authority', type=valid_authority, location='json', required=True)
        self.reqparse.add_argument('description', type=str, location='json')
        self.reqparse.add_argument('country', type=str, location='json', required=True)
        self.reqparse.add_argument('state', type=str, location='json', required=True)
        self.reqparse.add_argument('location', type=str, location='json', required=True)
        self.reqparse.add_argument('organization', type=str, location='json', required=True)
        self.reqparse.add_argument('organizationalUnit', type=str, location='json', required=True)
        self.reqparse.add_argument('owner', type=str, location='json', required=True)
        self.reqparse.add_argument('commonName', type=str, location='json', required=True)
        self.reqparse.add_argument('csr', type=str, location='json')

        args = self.reqparse.parse_args()

        authority = args['authority']
        role = role_service.get_by_name(authority.owner)

        # all the authority role members should be allowed
        roles = [x.name for x in authority.roles]

        # allow "owner" roles by team DL
        roles.append(role)
        authority_permission = AuthorityPermission(authority.id, roles)

        if authority_permission.can():
            # if we are not admins lets make sure we aren't issuing anything sensitive
            if not SensitiveDomainPermission().can():
                check_sensitive_domains(get_domains_from_options(args))
            return service.create(**args)

        return dict(message="You are not authorized to use {0}".format(args['authority'].name)), 403