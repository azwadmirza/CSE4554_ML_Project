def list_values(hive, key=None, use_32bit_registry=False, include_default=True):
    '''
    Enumerates the values in a registry key or hive.

    :param str hive: The name of the hive. Can be one of the following

        - HKEY_LOCAL_MACHINE or HKLM
        - HKEY_CURRENT_USER or HKCU
        - HKEY_USER or HKU
        - HKEY_CLASSES_ROOT or HKCR
        - HKEY_CURRENT_CONFIG or HKCC

    :param str key: The key (looks like a path) to the value name. If a key is
        not passed, the values under the hive will be returned.

    :param bool use_32bit_registry: Accesses the 32bit portion of the registry
        on 64 bit installations. On 32bit machines this is ignored.

    :param bool include_default: Toggle whether to include the '(Default)' value.

    :return: A list of values under the hive or key.
    :rtype: list

    CLI Example:

    .. code-block:: bash

        salt '*' reg.list_values HKLM 'SYSTEM\\CurrentControlSet\\Services\\Tcpip'
    '''
    local_hive = _to_unicode(hive)
    local_key = _to_unicode(key)

    registry = Registry()
    hkey = registry.hkeys[local_hive]
    access_mask = registry.registry_32[use_32bit_registry]
    handle = None
    values = list()

    try:
        handle = win32api.RegOpenKeyEx(hkey, local_key, 0, access_mask)

        for i in range(win32api.RegQueryInfoKey(handle)[1]):
            vname, vdata, vtype = win32api.RegEnumValue(handle, i)

            if not vname:
                vname = "(Default)"

            value = {'hive':   local_hive,
                     'key':    local_key,
                     'vname':  _to_mbcs(vname),
                     'vtype':  registry.vtype_reverse[vtype],
                     'success': True}
            # Only convert text types to unicode
            if vtype == win32con.REG_MULTI_SZ:
                value['vdata'] = [_to_mbcs(i) for i in vdata]
            elif vtype in [win32con.REG_SZ, win32con.REG_EXPAND_SZ]:
                value['vdata'] = _to_mbcs(vdata)
            else:
                value['vdata'] = vdata
            values.append(value)
    except Exception as exc:  # pylint: disable=E0602
        log.debug(r'Cannot find key: %s\%s', hive, key, exc_info=True)
        return False, r'Cannot find key: {0}\{1}'.format(hive, key)
    finally:
        if handle:
            handle.Close()
    return values