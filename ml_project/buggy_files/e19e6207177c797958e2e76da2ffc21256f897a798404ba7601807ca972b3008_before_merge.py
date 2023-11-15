def write_pem(text, path, overwrite=True, pem_type=None):
    """
    Writes out a PEM string fixing any formatting or whitespace
    issues before writing.

    text:
        PEM string input to be written out.

    path:
        Path of the file to write the PEM out to.

    overwrite:
        If ``True`` (default), write_pem will overwrite the entire PEM file.
        Set False to preserve existing private keys and dh params that may
        exist in the PEM file.

    pem_type:
        The PEM type to be saved, for example ``CERTIFICATE`` or
        ``PUBLIC KEY``. Adding this will allow the function to take
        input that may contain multiple PEM types.

    CLI Example:

    .. code-block:: bash

        salt '*' x509.write_pem "-----BEGIN CERTIFICATE-----MIIGMzCCBBugA..." path=/etc/pki/mycert.crt
    """
    with salt.utils.files.set_umask(0o077):
        text = get_pem_entry(text, pem_type=pem_type)
        _dhparams = ""
        _private_key = ""
        if (
            pem_type
            and pem_type == "CERTIFICATE"
            and os.path.isfile(path)
            and not overwrite
        ):
            _filecontents = _text_or_file(path)
            try:
                _dhparams = get_pem_entry(_filecontents, "DH PARAMETERS")
            except salt.exceptions.SaltInvocationError as err:
                log.debug("Error when getting DH PARAMETERS: %s", err)
                log.trace(err, exc_info=err)
            try:
                _private_key = get_pem_entry(_filecontents, "(?:RSA )?PRIVATE KEY")
            except salt.exceptions.SaltInvocationError as err:
                log.debug("Error when getting PRIVATE KEY: %s", err)
                log.trace(err, exc_info=err)
        with salt.utils.files.fopen(path, "w") as _fp:
            if pem_type and pem_type == "CERTIFICATE" and _private_key:
                _fp.write(salt.utils.stringutils.to_str(_private_key))
            _fp.write(salt.utils.stringutils.to_str(text))
            if pem_type and pem_type == "CERTIFICATE" and _dhparams:
                _fp.write(salt.utils.stringutils.to_str(_dhparams))
    return "PEM written to {0}".format(path)