def create_csr(ca_name,
               bits=2048,
               CN='localhost',
               C='US',
               ST='Utah',
               L='Salt Lake City',
               O='SaltStack',
               OU=None,
               emailAddress='xyz@pdq.net',
               subjectAltName=None,
               cacert_path=None,
               ca_filename=None,
               csr_path=None,
               csr_filename=None,
               digest='sha256'):
    '''
    Create a Certificate Signing Request (CSR) for a
    particular Certificate Authority (CA)

    ca_name
        name of the CA
    bits
        number of RSA key bits, default is 2048
    CN
        common name in the request, default is "localhost"
    C
        country, default is "US"
    ST
        state, default is "Utah"
    L
        locality, default is "Centerville", the city where SaltStack originated
    O
        organization, default is "SaltStack"
        NOTE: Must the same as CA certificate or an error will be raised
    OU
        organizational unit, default is None
    emailAddress
        email address for the request, default is 'xyz@pdq.net'
    subjectAltName
        valid subjectAltNames in full form, e.g. to add DNS entry you would call
        this function with this value:

        examples: ['DNS:somednsname.com',
                'DNS:1.2.3.4',
                'IP:1.2.3.4',
                'IP:2001:4801:7821:77:be76:4eff:fe11:e51',
                'email:me@i.like.pie.com']

    .. note::
        some libraries do not properly query IP: prefixes, instead looking
        for the given req. source with a DNS: prefix. To be thorough, you
        may want to include both DNS: and IP: entries if you are using
        subjectAltNames for destinations for your TLS connections.
            e.g.:
                requests to https://1.2.3.4 will fail from python's
                requests library w/out the second entry in the above list

    cacert_path
        absolute path to ca certificates root directory
    ca_filename
        alternative filename for the CA
    csr_path
        full path to the CSR directory
    csr_filename
        alternative filename for the csr, useful when using special characters in the CN
    digest
        The message digest algorithm. Must be a string describing a digest
        algorithm supported by OpenSSL (by EVP_get_digestbyname, specifically).
        For example, "md5" or "sha1". Default: 'sha256'

    Writes out a Certificate Signing Request (CSR) If the file already
    exists, the function just returns assuming the CSR already exists.

    If the following values were set::

        ca.cert_base_path='/etc/pki'
        ca_name='koji'
        CN='test.egavas.org'

    the resulting CSR, and corresponding key, would be written in the
    following location::

        /etc/pki/koji/certs/test.egavas.org.csr
        /etc/pki/koji/certs/test.egavas.org.key

    CLI Example:

    .. code-block:: bash

        salt '*' tls.create_csr test
    '''
    set_ca_path(cacert_path)

    if not ca_filename:
        ca_filename = '{0}_ca_cert'.format(ca_name)

    if not ca_exists(ca_name, ca_filename=ca_filename):
        return ('Certificate for CA named "{0}" does not exist, please create '
                'it first.').format(ca_name)

    if not csr_path:
        csr_path = '{0}/{1}/certs/'.format(cert_base_path(), ca_name)

    if not os.path.exists(csr_path):
        os.makedirs(csr_path)

    if not csr_filename:
        csr_filename = CN

    csr_f = '{0}/{1}.csr'.format(csr_path, csr_filename)

    if os.path.exists(csr_f):
        return 'Certificate Request "{0}" already exists'.format(csr_f)

    key = OpenSSL.crypto.PKey()
    key.generate_key(OpenSSL.crypto.TYPE_RSA, bits)

    req = OpenSSL.crypto.X509Req()

    req.get_subject().C = C
    req.get_subject().ST = ST
    req.get_subject().L = L
    req.get_subject().O = O
    if OU:
        req.get_subject().OU = OU
    req.get_subject().CN = CN
    req.get_subject().emailAddress = emailAddress

    extensions = get_extensions('server')['csr']
    extension_adds = []

    for ext, value in extensions.items():
        extension_adds.append(OpenSSL.crypto.X509Extension(ext, False, value))

    if subjectAltName:
        if isinstance(subjectAltName, str):
            subjectAltName = [subjectAltName]

        extension_adds.append(
            OpenSSL.crypto.X509Extension(
                'subjectAltName', False, ", ".join(subjectAltName)))

    req.add_extensions(extension_adds)
    req.set_pubkey(key)
    req.sign(key, digest)

    # Write private key and request
    with salt.utils.fopen('{0}/{1}.key'.format(csr_path,
                                               csr_filename), 'w+') as priv_key:
        priv_key.write(
                OpenSSL.crypto.dump_privatekey(OpenSSL.crypto.FILETYPE_PEM, key)
                )

    with salt.utils.fopen(csr_f, 'w+') as csr:
        csr.write(
                OpenSSL.crypto.dump_certificate_request(
                    OpenSSL.crypto.FILETYPE_PEM,
                    req
                    )
                )

    ret = 'Created Private Key: "{0}/{1}.key." '.format(
                    csr_path,
                    csr_filename
                    )
    ret += 'Created CSR for "{0}": "{1}/{2}.csr."'.format(
                    CN,
                    csr_path,
                    csr_filename
                    )

    return ret