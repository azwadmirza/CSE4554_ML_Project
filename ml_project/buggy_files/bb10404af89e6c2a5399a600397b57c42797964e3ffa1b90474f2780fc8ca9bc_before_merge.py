def sign_remote_certificate(argdic, **kwargs):
    """
    Request a certificate to be remotely signed according to a signing policy.

    argdic:
        A dict containing all the arguments to be passed into the
        create_certificate function. This will become kwargs when passed
        to create_certificate.

    kwargs:
        kwargs delivered from publish.publish

    CLI Example:

    .. code-block:: bash

        salt '*' x509.sign_remote_certificate argdic="{'public_key': '/etc/pki/www.key', 'signing_policy': 'www'}" __pub_id='www1'
    """
    if "signing_policy" not in argdic:
        return "signing_policy must be specified"

    if not isinstance(argdic, dict):
        argdic = ast.literal_eval(argdic)

    signing_policy = {}
    if "signing_policy" in argdic:
        signing_policy = _get_signing_policy(argdic["signing_policy"])
        if not signing_policy:
            return "Signing policy {0} does not exist.".format(argdic["signing_policy"])

        if isinstance(signing_policy, list):
            dict_ = {}
            for item in signing_policy:
                dict_.update(item)
            signing_policy = dict_

    if "minions" in signing_policy:
        if "__pub_id" not in kwargs:
            return "minion sending this request could not be identified"
        if not _match_minions(signing_policy["minions"], kwargs["__pub_id"]):
            return "{0} not permitted to use signing policy {1}".format(
                kwargs["__pub_id"], argdic["signing_policy"]
            )

    try:
        return create_certificate(path=None, text=True, **argdic)
    except Exception as except_:  # pylint: disable=broad-except
        return str(except_)