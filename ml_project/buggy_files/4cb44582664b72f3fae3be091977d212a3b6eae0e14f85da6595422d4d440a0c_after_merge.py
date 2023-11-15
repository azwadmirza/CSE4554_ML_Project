def certificate_managed(name, days_remaining=90, append_certs=None, **kwargs):
    """
    Manage a Certificate

    name
        Path to the certificate

    days_remaining : 90
        The minimum number of days remaining when the certificate should be
        recreated. A value of 0 disables automatic renewal.

    append_certs:
        A list of certificates to be appended to the managed file.

    kwargs:
        Any arguments supported by :py:func:`x509.create_certificate
        <salt.modules.x509.create_certificate>` or :py:func:`file.managed
        <salt.states.file.managed>` are supported.

    Examples:

    .. code-block:: yaml

        /etc/pki/ca.crt:
          x509.certificate_managed:
            - signing_private_key: /etc/pki/ca.key
            - CN: ca.example.com
            - C: US
            - ST: Utah
            - L: Salt Lake City
            - basicConstraints: "critical CA:true"
            - keyUsage: "critical cRLSign, keyCertSign"
            - subjectKeyIdentifier: hash
            - authorityKeyIdentifier: keyid,issuer:always
            - days_valid: 3650
            - days_remaining: 0
            - backup: True


    .. code-block:: yaml

        /etc/ssl/www.crt:
          x509.certificate_managed:
            - ca_server: pki
            - signing_policy: www
            - public_key: /etc/ssl/www.key
            - CN: www.example.com
            - days_valid: 90
            - days_remaining: 30
            - backup: True

    """
    if "path" in kwargs:
        name = kwargs.pop("path")

    if "ca_server" in kwargs and "signing_policy" not in kwargs:
        raise salt.exceptions.SaltInvocationError(
            "signing_policy must be specified if ca_server is."
        )

    if "public_key" not in kwargs and "signing_private_key" not in kwargs:
        raise salt.exceptions.SaltInvocationError(
            "public_key or signing_private_key must be specified."
        )

    ret = {"name": name, "result": False, "changes": {}, "comment": ""}

    is_valid, invalid_reason, current_cert_info = _certificate_is_valid(
        name, days_remaining, append_certs, **kwargs
    )

    if is_valid:
        ret["result"] = True
        ret["comment"] = "Certificate {0} is valid and up to date".format(name)
        return ret

    if __opts__["test"]:
        ret["result"] = None
        ret["comment"] = "Certificate {0} will be created".format(name)
        ret["changes"]["Status"] = {
            "Old": invalid_reason,
            "New": "Certificate will be valid and up to date",
        }
        return ret

    contents = __salt__["x509.create_certificate"](text=True, **kwargs)
    # Check the module actually returned a cert and not an error message as a string
    try:
        __salt__["x509.read_certificate"](contents)
    except salt.exceptions.SaltInvocationError as e:
        ret["result"] = False
        ret[
            "comment"
        ] = "An error occurred creating the certificate {0}. The result returned from x509.create_certificate is not a valid PEM file:\n{1}".format(
            name, str(e)
        )
        return ret

    if not append_certs:
        append_certs = []
    for append_file in append_certs:
        try:
            append_file_contents = __salt__["x509.get_pem_entry"](
                append_file, pem_type="CERTIFICATE"
            )
            contents += append_file_contents
        except salt.exceptions.SaltInvocationError as e:
            ret["result"] = False
            ret[
                "comment"
            ] = "{0} is not a valid certificate file, cannot append it to the certificate {1}.\nThe error returned by the x509 module was:\n{2}".format(
                append_file, name, str(e)
            )
            return ret

    file_args, extra_args = _get_file_args(name, **kwargs)
    file_args["contents"] = contents
    file_ret = __states__["file.managed"](**file_args)

    if file_ret["changes"]:
        ret["changes"] = {"File": file_ret["changes"]}

    ret["changes"]["Certificate"] = {
        "Old": current_cert_info,
        "New": __salt__["x509.read_certificate"](certificate=name),
    }
    ret["changes"]["Status"] = {
        "Old": invalid_reason,
        "New": "Certificate is valid and up to date",
    }
    ret["comment"] = "Certificate {0} is valid and up to date".format(name)
    ret["result"] = True

    return ret