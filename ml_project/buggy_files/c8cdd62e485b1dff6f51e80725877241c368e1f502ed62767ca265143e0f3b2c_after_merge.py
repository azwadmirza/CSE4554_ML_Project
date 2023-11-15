def account_check(username, password, request):
    parent_id = username
    try:
        existing = request.registry.storage.get(parent_id=parent_id,
                                                collection_id='account',
                                                object_id=username)
    except storage_exceptions.RecordNotFoundError:
        return None

    hashed = existing['password'].encode(encoding='utf-8')
    pwd_str = password.encode(encoding='utf-8')
    if hashed == bcrypt.hashpw(pwd_str, hashed):
        return True  # Match! Return anything but None.