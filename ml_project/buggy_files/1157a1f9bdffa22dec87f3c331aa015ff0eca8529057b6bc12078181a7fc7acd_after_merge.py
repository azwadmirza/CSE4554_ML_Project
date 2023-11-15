def setup_g():
    """Store commonly used values in Flask's special g object"""
    # ignore_static here because `crypto_util.shash` is bcrypt (very time consuming),
    # and we don't need to waste time running if we're just serving a static
    # resource that won't need to access these common values.
    if logged_in():
        # We use session.get (which defaults to None if 'flagged' is not in the
        # session) to avoid a KeyError on the redirect from login/ to lookup/
        g.flagged = session.get('flagged')
        g.codename = session['codename']
        g.sid = crypto_util.shash(g.codename)
        g.loc = store.path(g.sid)