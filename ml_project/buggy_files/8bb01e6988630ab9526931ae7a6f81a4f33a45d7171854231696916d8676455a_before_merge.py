def create_certificate(path=None, text=False, overwrite=True, ca_server=None, **kwargs):
    """
    Create an X509 certificate.

    path:
        Path to write the certificate to.

    text:
        If ``True``, return the PEM text without writing to a file.
        Default ``False``.

    overwrite:
        If ``True`` (default), create_certificate will overwrite the entire PEM
        file. Set False to preserve existing private keys and dh params that
        may exist in the PEM file.

    kwargs:
        Any of the properties below can be included as additional
        keyword arguments.

    ca_server:
        Request a remotely signed certificate from ca_server. For this to
        work, a ``signing_policy`` must be specified, and that same policy
        must be configured on the ca_server. See ``signing_policy`` for
        details. Also, the salt master must permit peers to call the
        ``sign_remote_certificate`` function.

        Example:

        /etc/salt/master.d/peer.conf

        .. code-block:: yaml

            peer:
              .*:
                - x509.sign_remote_certificate

    subject properties:
        Any of the values below can be included to set subject properties
        Any other subject properties supported by OpenSSL should also work.

        C:
            2 letter Country code
        CN:
            Certificate common name, typically the FQDN.

        Email:
            Email address

        GN:
            Given Name

        L:
            Locality

        O:
            Organization

        OU:
            Organization Unit

        SN:
            SurName

        ST:
            State or Province

    signing_private_key:
        A path or string of the private key in PEM format that will be used
        to sign this certificate. If neither ``signing_cert``, ``public_key``,
        or ``csr`` are included, it will be assumed that this is a self-signed
        certificate, and the public key matching ``signing_private_key`` will
        be used to create the certificate.

    signing_private_key_passphrase:
        Passphrase used to decrypt the signing_private_key.

    signing_cert:
        A certificate matching the private key that will be used to sign this
        certificate. This is used to populate the issuer values in the
        resulting certificate. Do not include this value for
        self-signed certificates.

    public_key:
        The public key to be included in this certificate. This can be sourced
        from a public key, certificate, CSR or private key. If a private key
        is used, the matching public key from the private key will be
        generated before any processing is done. This means you can request a
        certificate from a remote CA using a private key file as your
        public_key and only the public key will be sent across the network to
        the CA. If neither ``public_key`` or ``csr`` are specified, it will be
        assumed that this is a self-signed certificate, and the public key
        derived from ``signing_private_key`` will be used. Specify either
        ``public_key`` or ``csr``, not both. Because you can input a CSR as a
        public key or as a CSR, it is important to understand the difference.
        If you import a CSR as a public key, only the public key will be added
        to the certificate, subject or extension information in the CSR will
        be lost.

    public_key_passphrase:
        If the public key is supplied as a private key, this is the passphrase
        used to decrypt it.

    csr:
        A file or PEM string containing a certificate signing request. This
        will be used to supply the subject, extensions and public key of a
        certificate. Any subject or extensions specified explicitly will
        overwrite any in the CSR.

    basicConstraints:
        X509v3 Basic Constraints extension.

    extensions:
        The following arguments set X509v3 Extension values. If the value
        starts with ``critical``, the extension will be marked as critical.

        Some special extensions are ``subjectKeyIdentifier`` and
        ``authorityKeyIdentifier``.

        ``subjectKeyIdentifier`` can be an explicit value or it can be the
        special string ``hash``. ``hash`` will set the subjectKeyIdentifier
        equal to the SHA1 hash of the modulus of the public key in this
        certificate. Note that this is not the exact same hashing method used
        by OpenSSL when using the hash value.

        ``authorityKeyIdentifier`` Use values acceptable to the openssl CLI
        tools. This will automatically populate ``authorityKeyIdentifier``
        with the ``subjectKeyIdentifier`` of ``signing_cert``. If this is a
        self-signed cert these values will be the same.

        basicConstraints:
            X509v3 Basic Constraints

        keyUsage:
            X509v3 Key Usage

        extendedKeyUsage:
            X509v3 Extended Key Usage

        subjectKeyIdentifier:
            X509v3 Subject Key Identifier

        issuerAltName:
            X509v3 Issuer Alternative Name

        subjectAltName:
            X509v3 Subject Alternative Name

        crlDistributionPoints:
            X509v3 CRL Distribution Points

        issuingDistributionPoint:
            X509v3 Issuing Distribution Point

        certificatePolicies:
            X509v3 Certificate Policies

        policyConstraints:
            X509v3 Policy Constraints

        inhibitAnyPolicy:
            X509v3 Inhibit Any Policy

        nameConstraints:
            X509v3 Name Constraints

        noCheck:
            X509v3 OCSP No Check

        nsComment:
            Netscape Comment

        nsCertType:
            Netscape Certificate Type

    days_valid:
        The number of days this certificate should be valid. This sets the
        ``notAfter`` property of the certificate. Defaults to 365.

    version:
        The version of the X509 certificate. Defaults to 3. This is
        automatically converted to the version value, so ``version=3``
        sets the certificate version field to 0x2.

    serial_number:
        The serial number to assign to this certificate. If omitted a random
        serial number of size ``serial_bits`` is generated.

    serial_bits:
        The number of bits to use when randomly generating a serial number.
        Defaults to 64.

    algorithm:
        The hashing algorithm to be used for signing this certificate.
        Defaults to sha256.

    copypath:
        An additional path to copy the resulting certificate to. Can be used
        to maintain a copy of all certificates issued for revocation purposes.

    prepend_cn:
        If set to True, the CN and a dash will be prepended to the copypath's filename.

        Example:
            /etc/pki/issued_certs/www.example.com-DE:CA:FB:AD:00:00:00:00.crt

    signing_policy:
        A signing policy that should be used to create this certificate.
        Signing policies should be defined in the minion configuration, or in
        a minion pillar. It should be a YAML formatted list of arguments
        which will override any arguments passed to this function. If the
        ``minions`` key is included in the signing policy, only minions
        matching that pattern (see match.glob and match.compound) will be
        permitted to remotely request certificates from that policy.

        Example:

        .. code-block:: yaml

            x509_signing_policies:
              www:
                - minions: 'www*'
                - signing_private_key: /etc/pki/ca.key
                - signing_cert: /etc/pki/ca.crt
                - C: US
                - ST: Utah
                - L: Salt Lake City
                - basicConstraints: "critical CA:false"
                - keyUsage: "critical cRLSign, keyCertSign"
                - subjectKeyIdentifier: hash
                - authorityKeyIdentifier: keyid,issuer:always
                - days_valid: 90
                - copypath: /etc/pki/issued_certs/

        The above signing policy can be invoked with ``signing_policy=www``

    not_before:
        Initial validity date for the certificate. This date must be specified
        in the format '%Y-%m-%d %H:%M:%S'.

        .. versionadded:: Sodium

    not_after:
        Final validity date for the certificate. This date must be specified in
        the format '%Y-%m-%d %H:%M:%S'.

        .. versionadded:: Sodium

    CLI Example:

    .. code-block:: bash

        salt '*' x509.create_certificate path=/etc/pki/myca.crt signing_private_key='/etc/pki/myca.key' csr='/etc/pki/myca.csr'}
    """

    if (
        not path
        and not text
        and ("testrun" not in kwargs or kwargs["testrun"] is False)
    ):
        raise salt.exceptions.SaltInvocationError(
            "Either path or text must be specified."
        )
    if path and text:
        raise salt.exceptions.SaltInvocationError(
            "Either path or text must be specified, not both."
        )

    if "public_key_passphrase" not in kwargs:
        kwargs["public_key_passphrase"] = None
    if ca_server:
        if "signing_policy" not in kwargs:
            raise salt.exceptions.SaltInvocationError(
                "signing_policy must be specified"
                "if requesting remote certificate from ca_server {0}.".format(ca_server)
            )
        if "csr" in kwargs:
            kwargs["csr"] = get_pem_entry(
                kwargs["csr"], pem_type="CERTIFICATE REQUEST"
            ).replace("\n", "")
        if "public_key" in kwargs:
            # Strip newlines to make passing through as cli functions easier
            kwargs["public_key"] = salt.utils.stringutils.to_str(
                get_public_key(
                    kwargs["public_key"], passphrase=kwargs["public_key_passphrase"]
                )
            ).replace("\n", "")

        # Remove system entries in kwargs
        # Including listen_in and prerequired because they are not included
        # in STATE_INTERNAL_KEYWORDS
        # for salt 2014.7.2
        for ignore in list(_STATE_INTERNAL_KEYWORDS) + [
            "listen_in",
            "prerequired",
            "__prerequired__",
        ]:
            kwargs.pop(ignore, None)
        # TODO: Make timeout configurable in 3000
        certs = __salt__["publish.publish"](
            tgt=ca_server,
            fun="x509.sign_remote_certificate",
            arg=salt.utils.data.decode_dict(kwargs, to_str=True),
            timeout=30,
        )

        if not any(certs):
            raise salt.exceptions.SaltInvocationError(
                "ca_server did not respond"
                " salt master must permit peers to"
                " call the sign_remote_certificate function."
            )

        cert_txt = certs[ca_server]

        if path:
            return write_pem(
                text=cert_txt, overwrite=overwrite, path=path, pem_type="CERTIFICATE"
            )
        else:
            return cert_txt

    signing_policy = {}
    if "signing_policy" in kwargs:
        signing_policy = _get_signing_policy(kwargs["signing_policy"])
        if isinstance(signing_policy, list):
            dict_ = {}
            for item in signing_policy:
                dict_.update(item)
            signing_policy = dict_

    # Overwrite any arguments in kwargs with signing_policy
    kwargs.update(signing_policy)

    for prop, default in six.iteritems(CERT_DEFAULTS):
        if prop not in kwargs:
            kwargs[prop] = default

    cert = M2Crypto.X509.X509()

    # X509 Version 3 has a value of 2 in the field.
    # Version 2 has a value of 1.
    # https://tools.ietf.org/html/rfc5280#section-4.1.2.1
    cert.set_version(kwargs["version"] - 1)

    # Random serial number if not specified
    if "serial_number" not in kwargs:
        kwargs["serial_number"] = _dec2hex(random.getrandbits(kwargs["serial_bits"]))
    serial_number = int(kwargs["serial_number"].replace(":", ""), 16)
    # With Python3 we occasionally end up with an INT that is greater than a C
    # long max_value. This causes an overflow error due to a bug in M2Crypto.
    # See issue: https://gitlab.com/m2crypto/m2crypto/issues/232
    # Remove this after M2Crypto fixes the bug.
    if six.PY3:
        if salt.utils.platform.is_windows():
            INT_MAX = 2147483647
            if serial_number >= INT_MAX:
                serial_number -= int(serial_number / INT_MAX) * INT_MAX
        else:
            if serial_number >= sys.maxsize:
                serial_number -= int(serial_number / sys.maxsize) * sys.maxsize
    cert.set_serial_number(serial_number)

    # Handle not_before and not_after dates for custom certificate validity
    fmt = "%Y-%m-%d %H:%M:%S"
    if "not_before" in kwargs:
        try:
            time = datetime.datetime.strptime(kwargs["not_before"], fmt)
        except:
            raise salt.exceptions.SaltInvocationError(
                "not_before: {0} is not in required format {1}".format(
                    kwargs["not_before"], fmt
                )
            )

        # If we do not set an explicit timezone to this naive datetime object,
        # the M2Crypto code will assume it is from the local machine timezone
        # and will try to adjust the time shift.
        time = time.replace(tzinfo=M2Crypto.ASN1.UTC)
        asn1_not_before = M2Crypto.ASN1.ASN1_UTCTIME()
        asn1_not_before.set_datetime(time)
        cert.set_not_before(asn1_not_before)

    if "not_after" in kwargs:
        try:
            time = datetime.datetime.strptime(kwargs["not_after"], fmt)
        except:
            raise salt.exceptions.SaltInvocationError(
                "not_after: {0} is not in required format {1}".format(
                    kwargs["not_after"], fmt
                )
            )

        # Forcing the datetime to have an explicit tzinfo here as well.
        time = time.replace(tzinfo=M2Crypto.ASN1.UTC)
        asn1_not_after = M2Crypto.ASN1.ASN1_UTCTIME()
        asn1_not_after.set_datetime(time)
        cert.set_not_after(asn1_not_after)

    # Set validity dates
    # pylint: disable=no-member

    # if no 'not_before' or 'not_after' dates are setup, both of the following
    # dates will be the date of today. then the days_valid offset makes sense.

    not_before = M2Crypto.m2.x509_get_not_before(cert.x509)
    not_after = M2Crypto.m2.x509_get_not_after(cert.x509)

    # Only process the dynamic dates if start and end are not specified.
    if "not_before" not in kwargs:
        M2Crypto.m2.x509_gmtime_adj(not_before, 0)
    if "not_after" not in kwargs:
        valid_seconds = 60 * 60 * 24 * kwargs["days_valid"]  # 60s * 60m * 24 * days
        M2Crypto.m2.x509_gmtime_adj(not_after, valid_seconds)

    # pylint: enable=no-member

    # If neither public_key or csr are included, this cert is self-signed
    if "public_key" not in kwargs and "csr" not in kwargs:
        kwargs["public_key"] = kwargs["signing_private_key"]
        if "signing_private_key_passphrase" in kwargs:
            kwargs["public_key_passphrase"] = kwargs["signing_private_key_passphrase"]

    csrexts = {}
    if "csr" in kwargs:
        kwargs["public_key"] = kwargs["csr"]
        csr = _get_request_obj(kwargs["csr"])
        cert.set_subject(csr.get_subject())
        csrexts = read_csr(kwargs["csr"])["X509v3 Extensions"]

    cert.set_pubkey(
        get_public_key(
            kwargs["public_key"], passphrase=kwargs["public_key_passphrase"], asObj=True
        )
    )

    subject = cert.get_subject()

    # pylint: disable=unused-variable
    for entry, num in six.iteritems(subject.nid):
        if entry in kwargs:
            setattr(subject, entry, kwargs[entry])
    # pylint: enable=unused-variable

    if "signing_cert" in kwargs:
        signing_cert = _get_certificate_obj(kwargs["signing_cert"])
    else:
        signing_cert = cert
    cert.set_issuer(signing_cert.get_subject())

    for extname, extlongname in six.iteritems(EXT_NAME_MAPPINGS):
        if (
            extname in kwargs
            or extlongname in kwargs
            or extname in csrexts
            or extlongname in csrexts
        ) is False:
            continue

        # Use explicitly set values first, fall back to CSR values.
        extval = (
            kwargs.get(extname)
            or kwargs.get(extlongname)
            or csrexts.get(extname)
            or csrexts.get(extlongname)
        )

        critical = False
        if extval.startswith("critical "):
            critical = True
            extval = extval[9:]

        if extname == "subjectKeyIdentifier" and "hash" in extval:
            extval = extval.replace("hash", _get_pubkey_hash(cert))

        issuer = None
        if extname == "authorityKeyIdentifier":
            issuer = signing_cert

        if extname == "subjectAltName":
            extval = extval.replace("IP Address", "IP")

        ext = _new_extension(
            name=extname, value=extval, critical=critical, issuer=issuer
        )
        if not ext.x509_ext:
            log.info("Invalid X509v3 Extension. {0}: {1}".format(extname, extval))
            continue

        cert.add_ext(ext)

    if "signing_private_key_passphrase" not in kwargs:
        kwargs["signing_private_key_passphrase"] = None
    if "testrun" in kwargs and kwargs["testrun"] is True:
        cert_props = read_certificate(cert)
        cert_props["Issuer Public Key"] = get_public_key(
            kwargs["signing_private_key"],
            passphrase=kwargs["signing_private_key_passphrase"],
        )
        return cert_props

    if not verify_private_key(
        private_key=kwargs["signing_private_key"],
        passphrase=kwargs["signing_private_key_passphrase"],
        public_key=signing_cert,
    ):
        raise salt.exceptions.SaltInvocationError(
            "signing_private_key: {0} "
            "does no match signing_cert: {1}".format(
                kwargs["signing_private_key"], kwargs.get("signing_cert", "")
            )
        )

    cert.sign(
        _get_private_key_obj(
            kwargs["signing_private_key"],
            passphrase=kwargs["signing_private_key_passphrase"],
        ),
        kwargs["algorithm"],
    )

    if not verify_signature(cert, signing_pub_key=signing_cert):
        raise salt.exceptions.SaltInvocationError(
            "failed to verify certificate signature"
        )

    if "copypath" in kwargs:
        if "prepend_cn" in kwargs and kwargs["prepend_cn"] is True:
            prepend = six.text_type(kwargs["CN"]) + "-"
        else:
            prepend = ""
        write_pem(
            text=cert.as_pem(),
            path=os.path.join(
                kwargs["copypath"], prepend + kwargs["serial_number"] + ".crt"
            ),
            pem_type="CERTIFICATE",
        )

    if path:
        return write_pem(
            text=cert.as_pem(), overwrite=overwrite, path=path, pem_type="CERTIFICATE"
        )
    else:
        return salt.utils.stringutils.to_str(cert.as_pem())