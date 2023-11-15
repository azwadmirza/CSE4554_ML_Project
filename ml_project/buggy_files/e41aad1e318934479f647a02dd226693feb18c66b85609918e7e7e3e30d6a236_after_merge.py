def check_session_id_signature(session_id, secret_key=settings.secret_key_bytes(),
                               signed=settings.sign_sessions()):
    """Check the signature of a session ID, returning True if it's valid.

    The server uses this function to check whether a session ID
    was generated with the correct secret key. If signed sessions are disabled,
    this function always returns True.

    Args:
        session_id (str) : The session ID to check
        secret_key (str, optional) : Secret key (default: value of 'BOKEH_SECRET_KEY' env var)
        signed (bool, optional) : Whether to check anything (default: value of
                                  'BOKEH_SIGN_SESSIONS' env var)

    """
    secret_key = _ensure_bytes(secret_key)
    if signed:
        pieces = session_id.split('-', 1)
        if len(pieces) != 2:
            return False
        base_id = pieces[0]
        provided_signature = pieces[1]
        expected_signature = _signature(base_id, secret_key)
        # hmac.compare_digest() uses a string compare algorithm that doesn't
        # short-circuit so we don't allow timing analysis
        # encode_utf8 is used to ensure that strings have same encoding
        return hmac.compare_digest(encode_utf8(expected_signature), encode_utf8(provided_signature))
    else:
        return True