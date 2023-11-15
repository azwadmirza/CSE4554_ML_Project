def key_exists(hive, key, use_32bit_registry=False):
    '''
    Check that the key is found in the registry

    :param str hive: The hive to connect to.
    :param str key: The key to check
    :param bool use_32bit_registry: Look in the 32bit portion of the registry

    :return: Returns True if found, False if not found
    :rtype: bool
    '''
    local_hive = _to_unicode(hive)
    local_key = _to_unicode(key)

    registry = Registry()
    try:
        hkey = registry.hkeys[local_hive]
    except KeyError:
        raise CommandExecutionError('Invalid Hive: {0}'.format(local_hive))
    access_mask = registry.registry_32[use_32bit_registry]

    try:
        handle = win32api.RegOpenKeyEx(hkey, local_key, 0, access_mask)
        win32api.RegCloseKey(handle)
        return True
    except Exception:  # pylint: disable=E0602
        return False