def read_value(hive, key, vname=None, use_32bit_registry=False):
    r'''
    Reads a registry value entry or the default value for a key.

    :param str hive: The name of the hive. Can be one of the following

        - HKEY_LOCAL_MACHINE or HKLM
        - HKEY_CURRENT_USER or HKCU
        - HKEY_USER or HKU

    :param str key: The key (looks like a path) to the value name.

    :param str vname: The value name. These are the individual name/data pairs
       under the key. If not passed, the key (Default) value will be returned

    :param bool use_32bit_registry: Accesses the 32bit portion of the registry
       on 64bit installations. On 32bit machines this is ignored.

    :return: A dictionary containing the passed settings as well as the
       value_data if successful. If unsuccessful, sets success to False.

    :rtype: dict

    If vname is not passed:

    - Returns the first unnamed value (Default) as a string.
    - Returns none if first unnamed value is empty.
    - Returns False if key not found.

    CLI Example:

    .. code-block:: bash

        salt '*' reg.read_value HKEY_LOCAL_MACHINE 'SOFTWARE\Salt' 'version'
    '''

    # If no name is passed, the default value of the key will be returned
    # The value name is Default

    # Setup the return array
    if PY2:
        ret = {'hive':  _mbcs_to_unicode(hive),
               'key':   _mbcs_to_unicode(key),
               'vname': _mbcs_to_unicode(vname),
               'vdata': None,
               'success': True}
        local_hive = _mbcs_to_unicode(hive)
        local_key = _unicode_to_mbcs(key)
        local_vname = _unicode_to_mbcs(vname)

    else:
        ret = {'hive': hive,
               'key':  key,
               'vname': vname,
               'vdata': None,
               'success': True}
        local_hive = hive
        local_key = key
        local_vname = vname

    if not vname:
        ret['vname'] = '(Default)'

    registry = Registry()
    hkey = registry.hkeys[local_hive]
    access_mask = registry.registry_32[use_32bit_registry]

    try:
        handle = _winreg.OpenKey(hkey, local_key, 0, access_mask)
        try:
            # QueryValueEx returns unicode data
            vdata, vtype = _winreg.QueryValueEx(handle, local_vname)
            if vdata or vdata in [0, '']:
                ret['vtype'] = registry.vtype_reverse[vtype]
                ret['vdata'] = vdata
            else:
                ret['comment'] = 'Empty Value'
        except WindowsError:  # pylint: disable=E0602
            ret['vdata'] = ('(value not set)')
            ret['vtype'] = 'REG_SZ'
    except WindowsError as exc:  # pylint: disable=E0602
        log.debug(exc)
        log.debug('Cannot find key: {0}\\{1}'.format(local_hive, local_key))
        ret['comment'] = 'Cannot find key: {0}\\{1}'.format(local_hive, local_key)
        ret['success'] = False
    return ret