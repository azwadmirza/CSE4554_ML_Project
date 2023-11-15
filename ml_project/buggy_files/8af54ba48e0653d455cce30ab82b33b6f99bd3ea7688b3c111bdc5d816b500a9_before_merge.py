    def _subkeys(_key):
        '''
        Enumerate keys
        '''
        i = 0
        while True:
            try:
                subkey = _winreg.EnumKey(_key, i)
                yield subkey
                i += 1
            except WindowsError:  # pylint: disable=E0602
                break