def mint(issuer_options):
    """
    Minting is slightly different for each authority.
    Support for multiple authorities is handled by individual plugins.

    :param issuer_options:
    """
    authority = issuer_options['authority']

    issuer = plugins.get(authority.plugin_name)

    # allow the CSR to be specified by the user
    if not issuer_options.get('csr'):
        csr, private_key = create_csr(issuer_options)
    else:
        csr = issuer_options.get('csr')
        private_key = None

    issuer_options['creator'] = g.user.email
    cert_body, cert_chain = issuer.create_certificate(csr, issuer_options)

    cert = Certificate(cert_body, private_key, cert_chain)

    cert.user = g.user
    cert.authority = authority
    database.update(cert)
    return cert, private_key, cert_chain,