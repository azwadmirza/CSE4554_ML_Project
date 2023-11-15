    def __init__(self):
        self.hkeys = {
            'HKEY_CURRENT_USER':  _winreg.HKEY_CURRENT_USER,
            'HKEY_LOCAL_MACHINE': _winreg.HKEY_LOCAL_MACHINE,
            'HKEY_USERS': _winreg.HKEY_USERS,
            'HKCU': _winreg.HKEY_CURRENT_USER,
            'HKLM': _winreg.HKEY_LOCAL_MACHINE,
            'HKU':  _winreg.HKEY_USERS,
        }
        self.vtype = {
            'REG_BINARY':    _winreg.REG_BINARY,
            'REG_DWORD':     _winreg.REG_DWORD,
            'REG_EXPAND_SZ': _winreg.REG_EXPAND_SZ,
            'REG_MULTI_SZ':  _winreg.REG_MULTI_SZ,
            'REG_SZ':        _winreg.REG_SZ
        }
        self.opttype = {
            'REG_OPTION_NON_VOLATILE': _winreg.REG_OPTION_NON_VOLATILE,
            'REG_OPTION_VOLATILE':     _winreg.REG_OPTION_VOLATILE
        }
        # Return Unicode due to from __future__ import unicode_literals
        self.vtype_reverse = {
            _winreg.REG_BINARY:    'REG_BINARY',
            _winreg.REG_DWORD:     'REG_DWORD',
            _winreg.REG_EXPAND_SZ: 'REG_EXPAND_SZ',
            _winreg.REG_MULTI_SZ:  'REG_MULTI_SZ',
            _winreg.REG_SZ:        'REG_SZ'
        }
        self.opttype_reverse = {
            _winreg.REG_OPTION_NON_VOLATILE: 'REG_OPTION_NON_VOLATILE',
            _winreg.REG_OPTION_VOLATILE:     'REG_OPTION_VOLATILE'
        }
        # delete_key_recursive uses this to check the subkey contains enough \
        # as we do not want to remove all or most of the registry
        self.subkey_slash_check = {
            _winreg.HKEY_CURRENT_USER:  0,
            _winreg.HKEY_LOCAL_MACHINE: 1,
            _winreg.HKEY_USERS:         1
        }

        self.registry_32 = {
            True: _winreg.KEY_READ | _winreg.KEY_WOW64_32KEY,
            False: _winreg.KEY_READ,
            }