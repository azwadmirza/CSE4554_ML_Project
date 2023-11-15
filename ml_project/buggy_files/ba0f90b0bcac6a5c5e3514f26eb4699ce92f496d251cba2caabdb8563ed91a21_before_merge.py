def get_signing_policy(signing_policy_name):
    """
    Returns the details of a names signing policy, including the text of
    the public key that will be used to sign it. Does not return the
    private key.

    CLI Example:

    .. code-block:: bash

        salt '*' x509.get_signing_policy www
    """
    signing_policy = _get_signing_policy(signing_policy_name)
    if not signing_policy:
        return "Signing policy {0} does not exist.".format(signing_policy_name)
    if isinstance(signing_policy, list):
        dict_ = {}
        for item in signing_policy:
            dict_.update(item)
        signing_policy = dict_

    try:
        del signing_policy["signing_private_key"]
    except KeyError:
        pass

    try:
        signing_policy["signing_cert"] = get_pem_entry(
            signing_policy["signing_cert"], "CERTIFICATE"
        )
    except KeyError:
        pass

    return signing_policy