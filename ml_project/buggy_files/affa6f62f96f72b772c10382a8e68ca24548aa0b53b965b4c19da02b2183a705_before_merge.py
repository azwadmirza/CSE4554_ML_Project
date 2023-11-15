def read_crl(crl):
    """
    Returns a dict containing details of a certificate revocation list.
    Input can be a PEM string or file path.

    :depends:   - OpenSSL command line tool

    crl:
        A path or PEM encoded string containing the CRL to read.

    CLI Example:

    .. code-block:: bash

        salt '*' x509.read_crl /etc/pki/mycrl.crl
    """
    text = _text_or_file(crl)
    text = get_pem_entry(text, pem_type="X509 CRL")

    crltempfile = tempfile.NamedTemporaryFile(delete=True)
    crltempfile.write(salt.utils.stringutils.to_str(text))
    crltempfile.flush()
    crlparsed = _parse_openssl_crl(crltempfile.name)
    crltempfile.close()

    return crlparsed