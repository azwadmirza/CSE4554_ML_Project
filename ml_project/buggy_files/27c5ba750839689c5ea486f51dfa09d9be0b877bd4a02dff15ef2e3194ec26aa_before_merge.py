def generate_jwt_token(session_id: str,
                       secret_key: Optional[bytes] = settings.secret_key_bytes(),
                       signed: bool = settings.sign_sessions(),
                       extra_payload: Optional[Dict[str, Any]] = None,
                       expiration: int = 300) -> str:
    """Generates a JWT token given a session_id and additional payload.

    Args:
        session_id (str):
            The session id to add to the token

        secret_key (str, optional) :
            Secret key (default: value of BOKEH_SECRET_KEY environment varariable)

        signed (bool, optional) :
            Whether to sign the session ID (default: value of BOKEH_SIGN_SESSIONS
            envronment varariable)

        extra_payload (dict, optional) :
            Extra key/value pairs to include in the Bokeh session token

        expiration (int, optional) :
            Expiration time

    Returns:
        str
    """
    now = calendar.timegm(dt.datetime.now().utctimetuple())
    payload = {'session_id': session_id, 'session_expiry': now+expiration}
    if extra_payload:
        if "session_id" in extra_payload:
            raise RuntimeError("extra_payload for session tokens may not contain 'session_id'")
        payload.update(extra_payload)
    token = _base64_encode(json.dumps(payload))
    secret_key = _ensure_bytes(secret_key)
    if not signed:
        return token
    return token + '.' + _signature(token, secret_key)