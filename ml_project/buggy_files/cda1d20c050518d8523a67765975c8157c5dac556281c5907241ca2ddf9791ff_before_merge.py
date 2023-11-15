def delete_value(hive, key, vname=None, use_32bit_registry=False):
    '''
    Delete a registry value entry or the default value for a key.

    :param str hive: The name of the hive. Can be one of the following

        - HKEY_LOCAL_MACHINE or HKLM
        - HKEY_CURRENT_USER or HKCU
        - HKEY_USER or HKU
        - HKEY_CLASSES_ROOT or HKCR
        - HKEY_CURRENT_CONFIG or HKCC

    :param str key: The key (looks like a path) to the value name.

    :param str vname: The value name. These are the individual name/data pairs
        under the key. If not passed, the key (Default) value will be deleted.

    :param bool use_32bit_registry: Deletes the 32bit portion of the registry on
        64bit installations. On 32bit machines this is ignored.

    :return: Returns True if successful, None if the value didn't exist, and
        False if unsuccessful
    :rtype: bool

    CLI Example:

    .. code-block:: bash

        salt '*' reg.delete_value HKEY_CURRENT_USER 'SOFTWARE\\Salt' 'version'
    '''
    local_hive = _to_unicode(hive)
    local_key = _to_unicode(key)
    local_vname = _to_unicode(vname)

    registry = Registry()
    hkey = registry.hkeys[local_hive]
    access_mask = registry.registry_32[use_32bit_registry] | win32con.KEY_ALL_ACCESS

    try:
        handle = win32api.RegOpenKeyEx(hkey, local_key, 0, access_mask)
        win32api.RegDeleteValue(handle, local_vname)
        win32api.RegCloseKey(handle)
        broadcast_change()
        return True
    except Exception as exc:  # pylint: disable=E0602
        if exc.winerror == 2:
            return None
        else:
            log.error(exc, exc_info=True)
            log.error('Hive: %s', local_hive)
            log.error('Key: %s', local_key)
            log.error('ValueName: %s', local_vname)
            log.error('32bit Reg: %s', use_32bit_registry)
            return False