def verify_crl(crl, cert):
    """
    Validate a CRL against a certificate.
    Parses openssl command line output, this is a workaround for M2Crypto's
    inability to get them from CSR objects.

    crl:
        The CRL to verify

    cert:
        The certificate to verify the CRL against

    CLI Example:

    .. code-block:: bash

        salt '*' x509.verify_crl crl=/etc/pki/myca.crl cert=/etc/pki/myca.crt
    """
    if not salt.utils.path.which("openssl"):
        raise salt.exceptions.SaltInvocationError("openssl binary not found in path")
    crltext = _text_or_file(crl)
    crltext = get_pem_entry(crltext, pem_type="X509 CRL")
    crltempfile = tempfile.NamedTemporaryFile(delete=True)
    crltempfile.write(salt.utils.stringutils.to_str(crltext))
    crltempfile.flush()

    certtext = _text_or_file(cert)
    certtext = get_pem_entry(certtext, pem_type="CERTIFICATE")
    certtempfile = tempfile.NamedTemporaryFile(delete=True)
    certtempfile.write(salt.utils.stringutils.to_str(certtext))
    certtempfile.flush()

    cmd = "openssl crl -noout -in {0} -CAfile {1}".format(
        crltempfile.name, certtempfile.name
    )

    output = __salt__["cmd.run_stderr"](cmd)

    crltempfile.close()
    certtempfile.close()

    if "verify OK" in output:
        return True
    else:
        return False