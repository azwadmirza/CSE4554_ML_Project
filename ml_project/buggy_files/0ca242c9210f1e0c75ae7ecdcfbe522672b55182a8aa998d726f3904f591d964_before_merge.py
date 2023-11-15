def _new_extension(name, value, critical=0, issuer=None, _pyfree=1):
    """
    Create new X509_Extension, this is required because M2Crypto
    doesn't support getting the publickeyidentifier from the issuer
    to create the authoritykeyidentifier extension.
    """
    if name == "subjectKeyIdentifier" and value.strip("0123456789abcdefABCDEF:") != "":
        raise salt.exceptions.SaltInvocationError("value must be precomputed hash")

    # ensure name and value are bytes
    name = salt.utils.stringutils.to_str(name)
    value = salt.utils.stringutils.to_str(value)

    try:
        ctx = M2Crypto.m2.x509v3_set_nconf()
        _fix_ctx(ctx, issuer)
        if ctx is None:
            raise MemoryError("Not enough memory when creating a new X509 extension")
        x509_ext_ptr = M2Crypto.m2.x509v3_ext_conf(None, ctx, name, value)
        lhash = None
    except AttributeError:
        lhash = M2Crypto.m2.x509v3_lhash()
        ctx = M2Crypto.m2.x509v3_set_conf_lhash(lhash)
        # ctx not zeroed
        _fix_ctx(ctx, issuer)
        x509_ext_ptr = M2Crypto.m2.x509v3_ext_conf(lhash, ctx, name, value)
    # ctx,lhash freed

    if x509_ext_ptr is None:
        raise M2Crypto.X509.X509Error(
            "Cannot create X509_Extension with name '{0}' and value '{1}'".format(
                name, value
            )
        )
    x509_ext = M2Crypto.X509.X509_Extension(x509_ext_ptr, _pyfree)
    x509_ext.set_critical(critical)
    return x509_ext