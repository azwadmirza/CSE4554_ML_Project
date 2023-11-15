def certificate_managed(
    name, days_remaining=90, managed_private_key=None, append_certs=None, **kwargs
):
    """
    Manage a Certificate

    name
        Path to the certificate

    days_remaining : 90
        The minimum number of days remaining when the certificate should be
        recreated. A value of 0 disables automatic renewal.

    managed_private_key
        Manages the private key corresponding to the certificate. All of the
        arguments supported by :py:func:`x509.private_key_managed
        <salt.states.x509.private_key_managed>` are supported. If `name` is not
        specified or is the same as the name of the certificate, the private
        key and certificate will be written together in the same file.

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

    file_args, kwargs = _get_file_args(name, **kwargs)

    rotate_private_key = False
    new_private_key = False
    if managed_private_key:
        private_key_args = {
            "name": name,
            "new": False,
            "overwrite": False,
            "bits": 2048,
            "passphrase": None,
            "cipher": "aes_128_cbc",
            "verbose": True,
        }
        private_key_args.update(managed_private_key)
        kwargs["public_key_passphrase"] = private_key_args["passphrase"]

        if private_key_args["new"]:
            rotate_private_key = True
            private_key_args["new"] = False

        if _check_private_key(
            private_key_args["name"],
            bits=private_key_args["bits"],
            passphrase=private_key_args["passphrase"],
            new=private_key_args["new"],
            overwrite=private_key_args["overwrite"],
        ):
            private_key = __salt__["x509.get_pem_entry"](
                private_key_args["name"], pem_type="RSA PRIVATE KEY"
            )
        else:
            new_private_key = True
            private_key = __salt__["x509.create_private_key"](
                text=True,
                bits=private_key_args["bits"],
                passphrase=private_key_args["passphrase"],
                cipher=private_key_args["cipher"],
                verbose=private_key_args["verbose"],
            )

        kwargs["public_key"] = private_key

    current_days_remaining = 0
    current_comp = {}

    if os.path.isfile(name):
        try:
            current = __salt__["x509.read_certificate"](certificate=name)
            current_comp = copy.deepcopy(current)
            if "serial_number" not in kwargs:
                current_comp.pop("Serial Number")
                if "signing_cert" not in kwargs:
                    try:
                        current_comp["X509v3 Extensions"][
                            "authorityKeyIdentifier"
                        ] = re.sub(
                            r"serial:([0-9A-F]{2}:)*[0-9A-F]{2}",
                            "serial:--",
                            current_comp["X509v3 Extensions"]["authorityKeyIdentifier"],
                        )
                    except KeyError:
                        pass
            current_comp.pop("Not Before")
            current_comp.pop("MD5 Finger Print")
            current_comp.pop("SHA1 Finger Print")
            current_comp.pop("SHA-256 Finger Print")
            current_notafter = current_comp.pop("Not After")
            current_days_remaining = (
                datetime.datetime.strptime(current_notafter, "%Y-%m-%d %H:%M:%S")
                - datetime.datetime.now()
            ).days
            if days_remaining == 0:
                days_remaining = current_days_remaining - 1
        except salt.exceptions.SaltInvocationError:
            current = "{0} is not a valid Certificate.".format(name)
    else:
        current = "{0} does not exist.".format(name)

    if "ca_server" in kwargs and "signing_policy" not in kwargs:
        raise salt.exceptions.SaltInvocationError(
            "signing_policy must be specified if ca_server is."
        )

    new = __salt__["x509.create_certificate"](testrun=True, **kwargs)

    if isinstance(new, dict):
        new_comp = copy.deepcopy(new)
        new.pop("Issuer Public Key")
        if "serial_number" not in kwargs:
            new_comp.pop("Serial Number")
            if "signing_cert" not in kwargs:
                try:
                    new_comp["X509v3 Extensions"]["authorityKeyIdentifier"] = re.sub(
                        r"serial:([0-9A-F]{2}:)*[0-9A-F]{2}",
                        "serial:--",
                        new_comp["X509v3 Extensions"]["authorityKeyIdentifier"],
                    )
                except KeyError:
                    pass
        new_comp.pop("Not Before")
        new_comp.pop("Not After")
        new_comp.pop("MD5 Finger Print")
        new_comp.pop("SHA1 Finger Print")
        new_comp.pop("SHA-256 Finger Print")
        new_issuer_public_key = new_comp.pop("Issuer Public Key")
    else:
        new_comp = new

    new_certificate = False
    if (
        current_comp == new_comp
        and current_days_remaining > days_remaining
        and __salt__["x509.verify_signature"](name, new_issuer_public_key)
    ):
        certificate = __salt__["x509.get_pem_entry"](name, pem_type="CERTIFICATE")
    else:
        if rotate_private_key and not new_private_key:
            new_private_key = True
            private_key = __salt__["x509.create_private_key"](
                text=True,
                bits=private_key_args["bits"],
                verbose=private_key_args["verbose"],
            )
            kwargs["public_key"] = private_key
        new_certificate = True
        certificate = __salt__["x509.create_certificate"](text=True, **kwargs)

    file_args["contents"] = ""
    private_ret = {}
    if managed_private_key:
        if private_key_args["name"] == name:
            file_args["contents"] = private_key
        else:
            private_file_args = copy.deepcopy(file_args)
            unique_private_file_args, _ = _get_file_args(**private_key_args)
            private_file_args.update(unique_private_file_args)
            private_file_args["contents"] = private_key
            private_ret = __states__["file.managed"](**private_file_args)
            if not private_ret["result"]:
                return private_ret

    file_args["contents"] += salt.utils.stringutils.to_str(certificate)

    if not append_certs:
        append_certs = []
    for append_cert in append_certs:
        file_args["contents"] += __salt__["x509.get_pem_entry"](
            append_cert, pem_type="CERTIFICATE"
        )

    file_args["show_changes"] = False
    ret = __states__["file.managed"](**file_args)

    if ret["changes"]:
        ret["changes"] = {"Certificate": ret["changes"]}
    else:
        ret["changes"] = {}
    if private_ret and private_ret["changes"]:
        ret["changes"]["Private Key"] = private_ret["changes"]
    if new_private_key:
        ret["changes"]["Private Key"] = "New private key generated"
    if new_certificate:
        ret["changes"]["Certificate"] = {
            "Old": current,
            "New": __salt__["x509.read_certificate"](certificate=certificate),
        }

    return ret