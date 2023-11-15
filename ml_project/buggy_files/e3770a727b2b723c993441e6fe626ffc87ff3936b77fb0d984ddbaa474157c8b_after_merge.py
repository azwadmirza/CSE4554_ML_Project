def initialize_tracking(cookie_dir):
    global active_user
    active_user = User(cookie_dir)
    try:
        active_user.initialize()
    except Exception:
        logger.debug('Got an exception trying to initialize tracking',
                     exc_info=True)
        active_user = User(None)