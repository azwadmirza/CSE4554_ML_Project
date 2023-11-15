def bindkey(cls, keystrokes, longname):
    oldlongname = bindkeys._get(keystrokes, cls)
    if oldlongname:
        vd.warning('%s was already bound to %s' % (keystrokes, oldlongname))
    bindkeys.set(keystrokes, longname, cls)