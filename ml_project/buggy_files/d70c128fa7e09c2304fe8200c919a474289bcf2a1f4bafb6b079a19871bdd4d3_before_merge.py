def read_value(hive, key, vname=None, use_32bit_registry=False):
    r'''
    Reads a registry value entry or the default value for a key.

    :param str hive: The name of the hive. Can be one of the following

        - HKEY_LOCAL_MACHINE or HKLM
        - HKEY_CURRENT_USER or HKCU
        - HKEY_USER or HKU
        - HKEY_CLASSES_ROOT or HKCR
        - HKEY_CURRENT_CONFIG or HKCC

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
    local_hive = _to_unicode(hive)
    local_key = _to_unicode(key)
    local_vname = _to_unicode(vname)

    ret = {'hive':  local_hive,
           'key':   local_key,
           'vname': local_vname,
           'vdata': None,
           'success': True}

    if not vname:
        ret['vname'] = '(Default)'

    registry = Registry()
    hkey = registry.hkeys[local_hive]
    access_mask = registry.registry_32[use_32bit_registry]

    try:
        handle = win32api.RegOpenKeyEx(hkey, local_key, 0, access_mask)
        try:
            # RegQueryValueEx returns and accepts unicode data
            vdata, vtype = win32api.RegQueryValueEx(handle, local_vname)
            if vdata or vdata in [0, '']:
                # Only convert text types to unicode
                ret['vtype'] = registry.vtype_reverse[vtype]
                if vtype == win32con.REG_MULTI_SZ:
                    ret['vdata'] = [_to_mbcs(i) for i in vdata]
                elif vtype in [win32con.REG_SZ, win32con.REG_EXPAND_SZ]:
                    ret['vdata'] = _to_mbcs(vdata)
                else:
                    ret['vdata'] = vdata
            else:
                ret['comment'] = 'Empty Value'
        except Exception as exc:
            if exc.winerror == 2 and vname is None:
                ret['vdata'] = ('(value not set)')
                ret['vtype'] = 'REG_SZ'
            else:
                msg = 'Cannot find {0} in {1}\\{2}' \
                      ''.format(local_vname, local_hive, local_key)
                log.trace(exc)
                log.trace(msg)
                ret['comment'] = msg
                ret['success'] = False
    except Exception as exc:  # pylint: disable=E0602
        msg = 'Cannot find key: {0}\\{1}'.format(local_hive, local_key)
        log.trace(exc)
        log.trace(msg)
        ret['comment'] = msg
        ret['success'] = False
    return ret