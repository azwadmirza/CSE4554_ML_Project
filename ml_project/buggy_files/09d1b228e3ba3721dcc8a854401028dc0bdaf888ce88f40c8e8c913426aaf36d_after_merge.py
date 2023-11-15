    def __init__(self):
        self.hkeys = {
            'HKEY_CURRENT_USER':  win32con.HKEY_CURRENT_USER,
            'HKEY_LOCAL_MACHINE': win32con.HKEY_LOCAL_MACHINE,
            'HKEY_USERS': win32con.HKEY_USERS,
            'HKCU': win32con.HKEY_CURRENT_USER,
            'HKLM': win32con.HKEY_LOCAL_MACHINE,
            'HKU':  win32con.HKEY_USERS,
        }
        self.vtype = {
            'REG_BINARY':    win32con.REG_BINARY,
            'REG_DWORD':     win32con.REG_DWORD,
            'REG_EXPAND_SZ': win32con.REG_EXPAND_SZ,
            'REG_MULTI_SZ':  win32con.REG_MULTI_SZ,
            'REG_SZ':        win32con.REG_SZ,
            'REG_QWORD':     win32con.REG_QWORD
        }
        self.opttype = {
            'REG_OPTION_NON_VOLATILE': 0,
            'REG_OPTION_VOLATILE':     1
        }
        # Return Unicode due to from __future__ import unicode_literals
        self.vtype_reverse = {
            win32con.REG_BINARY:    'REG_BINARY',
            win32con.REG_DWORD:     'REG_DWORD',
            win32con.REG_EXPAND_SZ: 'REG_EXPAND_SZ',
            win32con.REG_MULTI_SZ:  'REG_MULTI_SZ',
            win32con.REG_SZ:        'REG_SZ',
            win32con.REG_QWORD:     'REG_QWORD'
        }
        self.opttype_reverse = {
            0: 'REG_OPTION_NON_VOLATILE',
            1: 'REG_OPTION_VOLATILE'
        }
        # delete_key_recursive uses this to check the subkey contains enough \
        # as we do not want to remove all or most of the registry
        self.subkey_slash_check = {
            win32con.HKEY_CURRENT_USER:  0,
            win32con.HKEY_LOCAL_MACHINE: 1,
            win32con.HKEY_USERS:         1
        }

        self.registry_32 = {
            True: win32con.KEY_READ | win32con.KEY_WOW64_32KEY,
            False: win32con.KEY_READ,
            }