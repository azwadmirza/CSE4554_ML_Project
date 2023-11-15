def setup_g():
    """Store commonly used values in Flask's special g object"""
    # ignore_static here because `crypto_util.shash` is bcrypt (very time consuming),
    # and we don't need to waste time running if we're just serving a static
    # resource that won't need to access these common values.
    if logged_in():
        g.flagged = session['flagged']
        g.codename = session['codename']
        g.sid = crypto_util.shash(g.codename)
        g.loc = store.path(g.sid)