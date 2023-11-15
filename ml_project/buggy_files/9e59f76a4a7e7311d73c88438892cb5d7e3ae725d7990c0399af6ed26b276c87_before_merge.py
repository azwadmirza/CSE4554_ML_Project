def delete_value(hive, key, vname=None, use_32bit_registry=False):
    '''
    Delete a registry value entry or the default value for a key.

    :param str hive: The name of the hive. Can be one of the following

        - HKEY_LOCAL_MACHINE or HKLM
        - HKEY_CURRENT_USER or HKCU
        - HKEY_USER or HKU

    :param str key: The key (looks like a path) to the value name.

    :param str vname: The value name. These are the individual name/data pairs
        under the key. If not passed, the key (Default) value will be deleted.

    :param bool use_32bit_registry: Deletes the 32bit portion of the registry on
        64bit installations. On 32bit machines this is ignored.

    :return: Returns True if successful, False if not
    :rtype: bool

    CLI Example:

    .. code-block:: bash

        salt '*' reg.delete_value HKEY_CURRENT_USER 'SOFTWARE\\Salt' 'version'
    '''

    if PY2:
        local_hive = _mbcs_to_unicode(hive)
        local_key = _unicode_to_mbcs(key)
        local_vname = _unicode_to_mbcs(vname)
    else:
        local_hive = hive
        local_key = key
        local_vname = vname

    registry = Registry()
    hkey = registry.hkeys[local_hive]
    access_mask = registry.registry_32[use_32bit_registry] | _winreg.KEY_ALL_ACCESS

    try:
        handle = _winreg.OpenKey(hkey, local_key, 0, access_mask)
        _winreg.DeleteValue(handle, local_vname)
        _winreg.CloseKey(handle)
        broadcast_change()
        return True
    except WindowsError as exc:  # pylint: disable=E0602
        log.error(exc, exc_info=True)
        log.error('Hive: {0}'.format(local_hive))
        log.error('Key: {0}'.format(local_key))
        log.error('ValueName: {0}'.format(local_vname))
        log.error('32bit Reg: {0}'.format(use_32bit_registry))
        return False