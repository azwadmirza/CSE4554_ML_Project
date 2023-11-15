def list_keys(hive, key=None, use_32bit_registry=False):
    '''
    Enumerates the subkeys in a registry key or hive.

    :param str hive: The name of the hive. Can be one of the following

        - HKEY_LOCAL_MACHINE or HKLM
        - HKEY_CURRENT_USER or HKCU
        - HKEY_USER or HKU

    :param str key: The key (looks like a path) to the value name. If a key is
        not passed, the keys under the hive will be returned.

    :param bool use_32bit_registry: Accesses the 32bit portion of the registry
        on 64 bit installations. On 32bit machines this is ignored.

    :return: A list of keys/subkeys under the hive or key.
    :rtype: list

    CLI Example:

    .. code-block:: bash

        salt '*' reg.list_keys HKLM 'SOFTWARE'
    '''

    if PY2:
        local_hive = _mbcs_to_unicode(hive)
        local_key = _unicode_to_mbcs(key)
    else:
        local_hive = hive
        local_key = key

    registry = Registry()
    hkey = registry.hkeys[local_hive]
    access_mask = registry.registry_32[use_32bit_registry]

    subkeys = []
    try:
        handle = _winreg.OpenKey(hkey, local_key, 0, access_mask)

        for i in range(_winreg.QueryInfoKey(handle)[0]):
            subkey = _winreg.EnumKey(handle, i)
            if PY2:
                subkeys.append(_mbcs_to_unicode(subkey))
            else:
                subkeys.append(subkey)

        handle.Close()

    except WindowsError as exc:  # pylint: disable=E0602
        log.debug(exc)
        log.debug('Cannot find key: {0}\\{1}'.format(hive, key))
        return False, 'Cannot find key: {0}\\{1}'.format(hive, key)

    return subkeys