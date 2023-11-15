def decryptPassword(cryptPass):
    hsm = _get_hsm()
    try:
        ret = hsm.decrypt_password(cryptPass)
    except Exception as exx:  # pragma: no cover
        log.warning(exx)
        ret = FAILED_TO_DECRYPT_PASSWORD
    return ret