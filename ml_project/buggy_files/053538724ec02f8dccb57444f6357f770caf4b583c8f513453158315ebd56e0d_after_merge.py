def _assert(condition, show_callers=True):
    '''A safer alternative to a bare assert.'''
    if g.unitTesting:
        assert condition
        return
    ok = bool(condition)
    if ok:
        return True
    print('')
    g.es_print('===== g._assert failed =====')
    print('')
    if show_callers:
        g.es_print(g.callers())
    return False