def delete_key_recursive(hive, key, use_32bit_registry=False):
    '''
    .. versionadded:: 2015.5.4

    Delete a registry key to include all subkeys.

    :param hive: The name of the hive. Can be one of the following

        - HKEY_LOCAL_MACHINE or HKLM
        - HKEY_CURRENT_USER or HKCU
        - HKEY_USER or HKU
        - HKEY_CLASSES_ROOT or HKCR
        - HKEY_CURRENT_CONFIG or HKCC

    :param key: The key to remove (looks like a path)

    :param bool use_32bit_registry: Deletes the 32bit portion of the registry on
        64bit installations. On 32bit machines this is ignored.

    :return: A dictionary listing the keys that deleted successfully as well as
        those that failed to delete.
    :rtype: dict

    The following example will remove ``salt`` and all its subkeys from the
    ``SOFTWARE`` key in ``HKEY_LOCAL_MACHINE``:

    CLI Example:

    .. code-block:: bash

        salt '*' reg.delete_key_recursive HKLM SOFTWARE\\salt
    '''

    local_hive = _to_unicode(hive)
    local_key = _to_unicode(key)

    # Instantiate the registry object
    registry = Registry()
    hkey = registry.hkeys[local_hive]
    key_path = local_key
    access_mask = registry.registry_32[use_32bit_registry] | win32con.KEY_ALL_ACCESS

    if not key_exists(local_hive, local_key, use_32bit_registry):
        return False

    if (len(key) > 1) and (key.count('\\', 1) < registry.subkey_slash_check[hkey]):
        log.error(
            'Hive:%s Key:%s; key is too close to root, not safe to remove',
            hive, key
        )
        return False

    # Functions for traversing the registry tree
    def _subkeys(_key):
        '''
        Enumerate keys
        '''
        i = 0
        while True:
            try:
                subkey = win32api.RegEnumKey(_key, i)
                yield _to_mbcs(subkey)
                i += 1
            except Exception:  # pylint: disable=E0602
                break

    def _traverse_registry_tree(_hkey, _keypath, _ret, _access_mask):
        '''
        Traverse the registry tree i.e. dive into the tree
        '''
        _key = win32api.RegOpenKeyEx(_hkey, _keypath, 0, _access_mask)
        for subkeyname in _subkeys(_key):
            subkeypath = '{0}\\{1}'.format(_keypath, subkeyname)
            _ret = _traverse_registry_tree(_hkey, subkeypath, _ret, access_mask)
            _ret.append(subkeypath)
        return _ret

    # Get a reverse list of registry keys to be deleted
    key_list = []
    key_list = _traverse_registry_tree(hkey, key_path, key_list, access_mask)
    # Add the top level key last, all subkeys must be deleted first
    key_list.append(key_path)

    ret = {'Deleted': [],
           'Failed': []}

    # Delete all sub_keys
    for sub_key_path in key_list:
        try:
            key_handle = win32api.RegOpenKeyEx(hkey, sub_key_path, 0, access_mask)
            win32api.RegDeleteKey(key_handle, '')
            ret['Deleted'].append(r'{0}\{1}'.format(hive, sub_key_path))
        except WindowsError as exc:  # pylint: disable=E0602
            log.error(exc, exc_info=True)
            ret['Failed'].append(r'{0}\{1} {2}'.format(hive, sub_key_path, exc))

    broadcast_change()

    return ret