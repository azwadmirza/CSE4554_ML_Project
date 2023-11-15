    def put(self, certificate_id):
        """
        .. http:put:: /certificates/1

           Update a certificate

           **Example request**:

           .. sourcecode:: http

              PUT /certificates/1 HTTP/1.1
              Host: example.com
              Accept: application/json, text/javascript

              {
                 "owner": "jimbob@example.com",
                 "active": false
                 "notifications": [],
                 "destinations": []
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
                "status": "unknown",
              }

           :reqheader Authorization: OAuth token to authenticate
           :statuscode 200: no error
           :statuscode 403: unauthenticated
        """
        self.reqparse.add_argument('active', type=bool, location='json')
        self.reqparse.add_argument('owner', type=str, location='json')
        self.reqparse.add_argument('description', type=str, location='json')
        self.reqparse.add_argument('destinations', type=list, default=[], location='json')
        self.reqparse.add_argument('notifications', type=list, default=[], location='json')
        args = self.reqparse.parse_args()

        cert = service.get(certificate_id)
        role = role_service.get_by_name(cert.owner)

        permission = UpdateCertificatePermission(certificate_id, getattr(role, 'name', None))

        if permission.can():
            return service.update(
                certificate_id,
                args['owner'],
                args['description'],
                args['active'],
                args['destinations'],
                args['notifications']
            )

        return dict(message='You are not authorized to update this certificate'), 403