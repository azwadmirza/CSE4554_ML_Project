def _assert(condition):
    '''A safer alternative to a bare assert.'''
    if g.unitTesting:
        assert condition
        return
    ok = bool(condition)
    if ok:
        return True
    g.es_print('g._assert failed')
    g.es_print(g.callers())
    return False