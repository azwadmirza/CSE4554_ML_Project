def validate_userid_signature(user: User) -> Optional[Address]:
    """ Validate a userId format and signature on displayName, and return its address"""
    # display_name should be an address in the USERID_RE format
    match = USERID_RE.match(user.user_id)
    if not match:
        return None

    msg = (
        "The User instance provided to validate_userid_signature must have the "
        "displayname attribute set. Make sure to warm the value using the "
        "DisplayNameCache."
    )
    displayname = user.displayname
    assert displayname is not None, msg

    encoded_address = match.group(1)
    address: Address = to_canonical_address(encoded_address)

    try:
        if DISPLAY_NAME_HEX_RE.match(displayname):
            signature_bytes = decode_hex(displayname)
        else:
            return None
        recovered = recover(data=user.user_id.encode(), signature=Signature(signature_bytes))
        if not (address and recovered and recovered == address):
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