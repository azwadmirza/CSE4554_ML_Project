def get_tops(extra_mods='', so_mods=''):
    tops = [
            os.path.dirname(salt.__file__),
            os.path.dirname(jinja2.__file__),
            os.path.dirname(yaml.__file__),
            os.path.dirname(tornado.__file__),
            os.path.dirname(msgpack.__file__),
            ]

    tops.append(six.__file__.replace('.pyc', '.py'))

    if HAS_CERTIFI:
        tops.append(os.path.dirname(certifi.__file__))

    if HAS_SINGLEDISPATCH:
        tops.append(singledispatch.__file__.replace('.pyc', '.py'))

    if HAS_SINGLEDISPATCH_HELPERS:
        tops.append(singledispatch_helpers.__file__.replace('.pyc', '.py'))

    if HAS_BACKPORTS_ABC:
        tops.append(backports_abc.__file__.replace('.pyc', '.py'))

    if HAS_SSL_MATCH_HOSTNAME:
        tops.append(os.path.dirname(os.path.dirname(ssl_match_hostname.__file__)))

    for mod in [m for m in extra_mods.split(',') if m]:
        if mod not in locals() and mod not in globals():
            try:
                locals()[mod] = __import__(mod)
                moddir, modname = os.path.split(locals()[mod].__file__)
                base, ext = os.path.splitext(modname)
                if base == '__init__':
                    tops.append(moddir)
                else:
                    tops.append(os.path.join(moddir, base + '.py'))
            except ImportError:
                # Not entirely sure this is the right thing, but the only
                # options seem to be 1) fail, 2) spew errors, or 3) pass.
                # Nothing else in here spits errors, and the markupsafe code
                # doesn't bail on import failure, so I followed that lead.
                # And of course, any other failure still S/T's.
                pass
    for mod in [m for m in so_mods.split(',') if m]:
        try:
            locals()[mod] = __import__(mod)
            tops.append(locals()[mod].__file__)
        except ImportError:
            pass   # As per comment above
    if HAS_MARKUPSAFE:
        tops.append(os.path.dirname(markupsafe.__file__))

    return tops