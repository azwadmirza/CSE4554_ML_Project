    def _traverse_registry_tree(_hkey, _keypath, _ret, _access_mask):
        '''
        Traverse the registry tree i.e. dive into the tree
        '''
        _key = win32api.RegOpenKeyEx(_hkey, _keypath, 0, _access_mask)
        for subkeyname in _subkeys(_key):
            subkeypath = r'{0}\{1}'.format(_keypath, subkeyname)
            _ret = _traverse_registry_tree(_hkey, subkeypath, _ret, access_mask)
            _ret.append('{0}'.format(subkeypath))
        return _ret