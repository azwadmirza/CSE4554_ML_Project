def list_values(hive, key=None, use_32bit_registry=False, include_default=True):
    '''
    Enumerates the values in a registry key or hive.

    :param str hive: The name of the hive. Can be one of the following

        - HKEY_LOCAL_MACHINE or HKLM
        - HKEY_CURRENT_USER or HKCU
        - HKEY_USER or HKU

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

    if PY2:
        local_hive = _mbcs_to_unicode(hive)
        local_key = _unicode_to_mbcs(key)
    else:
        local_hive = hive
        local_key = key

    registry = Registry()
    hkey = registry.hkeys[local_hive]
    access_mask = registry.registry_32[use_32bit_registry]
    handle = None
    values = list()

    try:
        handle = _winreg.OpenKey(hkey, local_key, 0, access_mask)

        for i in range(_winreg.QueryInfoKey(handle)[1]):
            vname, vdata, vtype = _winreg.EnumValue(handle, i)

            value = {'hive':   local_hive,
                     'key':    local_key,
                     'vname':  vname,
                     'vdata':  vdata,
                     'vtype':  registry.vtype_reverse[vtype],
                     'success': True}
            values.append(value)
        if include_default:
            # Get the default value for the key
            value = {'hive':    local_hive,
                     'key':     local_key,
                     'vname':   '(Default)',
                     'vdata':   None,
                     'success': True}
            try:
                # QueryValueEx returns unicode data
                vdata, vtype = _winreg.QueryValueEx(handle, '(Default)')
                if vdata or vdata in [0, '']:
                    value['vtype'] = registry.vtype_reverse[vtype]
                    value['vdata'] = vdata
                else:
                    value['comment'] = 'Empty Value'
            except WindowsError:  # pylint: disable=E0602
                value['vdata'] = ('(value not set)')
                value['vtype'] = 'REG_SZ'
            values.append(value)
    except WindowsError as exc:  # pylint: disable=E0602
        log.debug(exc)
        log.debug(r'Cannot find key: {0}\{1}'.format(hive, key))
        return False, r'Cannot find key: {0}\{1}'.format(hive, key)
    finally:
        if handle:
            handle.Close()
    return values