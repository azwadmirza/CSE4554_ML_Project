def validate_userid_signature(user: User) -> Optional[Address]:
    """ Validate a userId format and signature on displayName, and return its address"""
    # display_name should be an address in the USERID_RE format
    match = USERID_RE.match(user.user_id)
    if not match:
        log.warning("Invalid user id", user=user.user_id)
        return None

    displayname = user.displayname

    if displayname is None:
        log.warning("Displayname not set", user=user.user_id)
        return None

    encoded_address = match.group(1)
    address: Address = to_canonical_address(encoded_address)

    try:
        if DISPLAY_NAME_HEX_RE.match(displayname):
            signature_bytes = decode_hex(displayname)
        else:
            log.warning("Displayname invalid format", user=user.user_id, displayname=displayname)
            return None
        recovered = recover(data=user.user_id.encode(), signature=Signature(signature_bytes))
        if not (address and recovered and recovered == address):
            log.warning("Unexpected signer of displayname", user=user.user_id)
            return None
    except (
        DecodeError,
        TypeError,
        InvalidSignature,
        MatrixRequestError,
        json.decoder.JSONDecodeError,
    ):
        return None
    return address