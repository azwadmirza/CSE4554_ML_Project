def lookup():
    msgs = []
    flagged = False
    for fn in os.listdir(g.loc):
        # TODO: make 'flag' a db column, so we can replace this with a db
        # lookup in the future
        if fn == '_FLAG':
            flagged = True
            continue
        if fn.startswith('reply-'):
            msgs.append(dict(
                id=fn,
                date=str(
                    datetime.fromtimestamp(
                        os.stat(store.path(g.sid, fn)).st_mtime)),
                msg=crypto_util.decrypt(
                    g.sid, g.codename, file(store.path(g.sid, fn)).read())
            ))
    if flagged:
        session['flagged'] = True

    def async_genkey(sid, codename):
        with app.app_context():
            background.execute(lambda: crypto_util.genkeypair(sid, codename))

    # Generate a keypair to encrypt replies from the journalist
    # Only do this if the journalist has flagged the source as one
    # that they would like to reply to. (Issue #140.)
    if not crypto_util.getkey(g.sid) and flagged:
        async_genkey(g.sid, g.codename)

    return render_template(
        'lookup.html', codename=g.codename, msgs=msgs, flagged=flagged,
        haskey=crypto_util.getkey(g.sid))