def _get_hg_root(q):
    _curpwd = os.getcwd()
    while True:
        if any([b.name == '.hg' for b in os.scandir(_curpwd)]):
            q.put(_curpwd)
            break
        else:
            _oldpwd = _curpwd
            _curpwd = os.path.split(_curpwd)[0]
            if _oldpwd == _curpwd:
                return False