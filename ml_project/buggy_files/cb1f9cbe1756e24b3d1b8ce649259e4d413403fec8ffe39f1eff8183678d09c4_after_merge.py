def decryptPassword(cryptPass, convert_unicode=False):
    """
    Decrypt the encrypted password ``cryptPass`` and return it.
    If an error occurs during decryption, return FAILED_TO_DECRYPT_PASSWORD.

    :param cryptPass: bytestring
    :param convert_unicode: If true, interpret the decrypted password as an UTF-8 string
                            and convert it to unicode. If an error occurs here,
                            the original bytestring is returned.
    """
    # NOTE: Why do we have the ``convert_unicode`` parameter?
    # Up until now, this always returned bytestrings. However, this breaks
    # LDAP and SQL resolvers, which expect this to return an unicode string
    # (and this makes more sense, because ``encryptPassword`` also
    # takes unicode strings!). But always returning unicode might break
    # other call sites of ``decryptPassword``. So we add the
    # keyword argument to avoid breaking compatibility.
    from privacyidea.lib.utils import to_unicode
    hsm = _get_hsm()
    try:
        ret = hsm.decrypt_password(cryptPass)
    except Exception as exx:  # pragma: no cover
        log.warning(exx)
        ret = FAILED_TO_DECRYPT_PASSWORD
    try:
        if convert_unicode:
            ret = to_unicode(ret)
    except Exception as exx:  # pragma: no cover
        log.warning(exx)
        # just keep ``ret`` as a bytestring in that case
    return ret