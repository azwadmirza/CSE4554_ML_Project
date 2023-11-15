def create_crl(path=None, text=False, signing_private_key=None,
        signing_cert=None, revoked=None, include_expired=False,
        days_valid=100):
    '''
    Create a CRL

    :depends:   - PyOpenSSL Python module

    path:
        Path to write the crl to.

    text:
        If ``True``, return the PEM text without writing to a file. Default ``False``.

    signing_private_key:
        A path or string of the private key in PEM format that will be used to sign this crl.
        This is required.

    signing_cert:
        A certificate matching the private key that will be used to sign this crl. This is
        required.

    revoked:
        A list of dicts containing all the certificates to revoke. Each dict represents one
        certificate. A dict must contain either the key ``serial_number`` with the value of
        the serial number to revoke, or ``certificate`` with either the PEM encoded text of
        the certificate, or a path ot the certificate to revoke.

        The dict can optionally contain the ``revocation_date`` key. If this key is omitted
        the revocation date will be set to now. If should be a string in the format "%Y-%m-%d %H:%M:%S".

        The dict can also optionally contain the ``not_after`` key. This is redundant if the
        ``certificate`` key is included. If the ``Certificate`` key is not included, this
        can be used for the logic behind the ``include_expired`` parameter.
        If should be a string in the format "%Y-%m-%d %H:%M:%S".

        The dict can also optionally contain the ``reason`` key. This is the reason code for the
        revocation. Available choices are ``unspecified``, ``keyCompromise``, ``CACompromise``,
        ``affiliationChanged``, ``superseded``, ``cessationOfOperation`` and ``certificateHold``.

    include_expired:
        Include expired certificates in the CRL. Default is ``False``.

    days_valid:
        The number of days that the CRL should be valid. This sets the Next Update field in the CRL.

    .. note

        At this time the pyOpenSSL library does not allow choosing a signing algorithm for CRLs
        See https://github.com/pyca/pyopenssl/issues/159

    CLI Example:

    .. code-block:: bash

        salt '*' x509.create_crl path=/etc/pki/mykey.key signing_private_key=/etc/pki/ca.key \\
                signing_cert=/etc/pki/ca.crt \\
                revoked="{'compromized-web-key': {'certificate': '/etc/pki/certs/www1.crt', \\
                'revocation_date': '2015-03-01 00:00:00'}}"
    '''
    # pyOpenSSL is required for dealing with CSLs. Importing inside these functions because
    # Client operations like creating CRLs shouldn't require pyOpenSSL
    # Note due to current limitations in pyOpenSSL it is impossible to specify a digest
    # For signing the CRL. This will hopefully be fixed soon: https://github.com/pyca/pyopenssl/pull/161
    import OpenSSL
    crl = OpenSSL.crypto.CRL()

    if revoked is None:
        revoked = []

    for rev_item in revoked:
        if 'certificate' in rev_item:
            rev_cert = read_certificate(rev_item['certificate'])
            rev_item['serial_number'] = rev_cert['Serial Number']
            rev_item['not_after'] = rev_cert['Not After']

        serial_number = rev_item['serial_number'].replace(':', '')
        serial_number = str(int(serial_number, 16))

        if 'not_after' in rev_item and not include_expired:
            not_after = datetime.datetime.strptime(rev_item['not_after'], '%Y-%m-%d %H:%M:%S')
            if datetime.datetime.now() > not_after:
                continue

        if 'revocation_date' not in rev_item:
            rev_item['revocation_date'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        rev_date = datetime.datetime.strptime(rev_item['revocation_date'], '%Y-%m-%d %H:%M:%S')
        rev_date = rev_date.strftime('%Y%m%d%H%M%SZ')

        rev = OpenSSL.crypto.Revoked()
        rev.set_serial(serial_number)
        rev.set_rev_date(rev_date)

        if 'reason' in rev_item:
            rev.set_reason(rev_item['reason'])

        crl.add_revoked(rev)

    signing_cert = _text_or_file(signing_cert)
    cert = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM,
            get_pem_entry(signing_cert, pem_type='CERTIFICATE'))
    signing_private_key = _text_or_file(signing_private_key)
    key = OpenSSL.crypto.load_privatekey(OpenSSL.crypto.FILETYPE_PEM,
            get_pem_entry(signing_private_key))

    crltext = crl.export(cert, key, OpenSSL.crypto.FILETYPE_PEM, days=days_valid)

    if text:
        return crltext

    return write_pem(text=crltext, path=path,
                pem_type='X509 CRL')