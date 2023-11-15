    def _subkeys(_key):
        '''
        Enumerate keys
        '''
        i = 0
        while True:
            try:
                subkey = win32api.RegEnumKey(_key, i)
                yield subkey
                i += 1
            except pywintypes.error:  # pylint: disable=E0602
                break