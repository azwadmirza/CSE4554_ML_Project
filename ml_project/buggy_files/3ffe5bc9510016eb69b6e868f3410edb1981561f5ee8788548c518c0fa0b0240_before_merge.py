    def POST(self, mid, keysize=None, force=None, **kwargs):
        r'''
        Easily generate keys for a minion and auto-accept the new key

        .. versionadded:: 2014.7.0

        Example partial kickstart script to bootstrap a new minion:

        .. code-block:: text

            %post
            mkdir -p /etc/salt/pki/minion
            curl -sSk https://localhost:8000/keys \
                    -d mid=jerry \
                    -d username=kickstart \
                    -d password=kickstart \
                    -d eauth=pam \
                | tar -C /etc/salt/pki/minion -xf -

            mkdir -p /etc/salt/minion.d
            printf 'master: 10.0.0.5\nid: jerry' > /etc/salt/minion.d/id.conf
            %end

        .. http:post:: /keys

            Generate a public and private key and return both as a tarball

            Authentication credentials must be passed in the request.

            :status 200: |200|
            :status 401: |401|
            :status 406: |406|

        **Example request:**

        .. code-block:: bash

            curl -sSk https://localhost:8000/keys \
                    -d mid=jerry \
                    -d username=kickstart \
                    -d password=kickstart \
                    -d eauth=pam \
                    -o jerry-salt-keys.tar

        .. code-block:: http

            POST /keys HTTP/1.1
            Host: localhost:8000

        **Example response:**

        .. code-block:: http

            HTTP/1.1 200 OK
            Content-Length: 10240
            Content-Disposition: attachment; filename="saltkeys-jerry.tar"
            Content-Type: application/x-tar

            jerry.pub0000644000000000000000000000070300000000000010730 0ustar  00000000000000
        '''
        lowstate = [{
            'client': 'wheel',
            'fun': 'key.gen_accept',
            'id_': mid,
        }]

        if keysize:
            lowstate[0]['keysize'] = keysize

        if force:
            lowstate[0]['force'] = force

        lowstate[0].update(kwargs)

        cherrypy.request.lowstate = lowstate
        result = self.exec_lowstate()
        ret = next(result, {}).get('data', {}).get('return', {})

        pub_key = ret.get('pub', '')
        pub_key_file = tarfile.TarInfo('minion.pub')
        pub_key_file.size = len(pub_key)

        priv_key = ret.get('priv', '')
        priv_key_file = tarfile.TarInfo('minion.pem')
        priv_key_file.size = len(priv_key)

        fileobj = StringIO.StringIO()
        tarball = tarfile.open(fileobj=fileobj, mode='w')
        tarball.addfile(pub_key_file, StringIO.StringIO(pub_key))
        tarball.addfile(priv_key_file, StringIO.StringIO(priv_key))
        tarball.close()

        headers = cherrypy.response.headers
        headers['Content-Disposition'] = 'attachment; filename="saltkeys-{0}.tar"'.format(mid)
        headers['Content-Type'] = 'application/x-tar'
        headers['Content-Length'] = fileobj.len
        headers['Cache-Control'] = 'no-cache'

        fileobj.seek(0)
        return fileobj