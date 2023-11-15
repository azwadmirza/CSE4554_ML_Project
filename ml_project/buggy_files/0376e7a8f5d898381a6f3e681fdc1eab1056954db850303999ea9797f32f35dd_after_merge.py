def present(name,
            vname=None,
            vdata=None,
            vtype='REG_SZ',
            use_32bit_registry=False):
    '''
    Ensure a registry key or value is present.

    :param str name: A string value representing the full path of the key to
    include the HIVE, Key, and all Subkeys. For example:

    ``HKEY_LOCAL_MACHINE\\SOFTWARE\\Salt``

    Valid hive values include:
    - HKEY_CURRENT_USER or HKCU
    - HKEY_LOCAL_MACHINE or HKLM
    - HKEY_USERS or HKU

    :param str vname: The name of the value you'd like to create beneath the
    Key. If this parameter is not passed it will assume you want to set the
    (Default) value

    :param str vdata: The value you'd like to set. If a value name (vname) is
    passed, this will be the data for that value name. If not, this will be the
    (Default) value for the key.

    The type for the (Default) value is always REG_SZ and cannot be changed.
    This parameter is optional. If not passed, the Key will be created with no
    associated item/value pairs.

    :param str vtype: The value type for the data you wish to store in the
    registry. Valid values are:

    - REG_BINARY
    - REG_DWORD
    - REG_EXPAND_SZ
    - REG_MULTI_SZ
    - REG_SZ (Default)

    :param bool use_32bit_registry: Use the 32bit portion of the registry.
    Applies only to 64bit windows. 32bit Windows will ignore this parameter.
    Default is False.

    :return: Returns a dictionary showing the results of the registry operation.
    :rtype: dict

    The following example will set the ``(Default)`` value for the
    ``SOFTWARE\\Salt`` key in the ``HKEY_CURRENT_USER`` hive to ``2016.3.1``:

    Example:

    .. code-block:: yaml

        HKEY_CURRENT_USER\\SOFTWARE\\Salt:
          reg.present:
            - vdata: 2016.3.1

    The following example will set the value for the ``version`` entry under the
    ``SOFTWARE\\Salt`` key in the ``HKEY_CURRENT_USER`` hive to ``2016.3.1``. The
    value will be reflected in ``Wow6432Node``:

    Example:

    .. code-block:: yaml

        HKEY_CURRENT_USER\\SOFTWARE\\Salt:
          reg.present:
            - vname: version
            - vdata: 2016.3.1

    In the above example the path is interpreted as follows:
    - ``HKEY_CURRENT_USER`` is the hive
    - ``SOFTWARE\\Salt`` is the key
    - ``vname`` is the value name ('version') that will be created under the key
    - ``vdata`` is the data that will be assigned to 'version'
    '''
    ret = {'name': name,
           'result': True,
           'changes': {},
           'comment': ''}

    hive, key = _parse_key(name)

    # Determine what to do
    reg_current = __utils__['reg.read_value'](hive=hive,
                                              key=key,
                                              vname=vname,
                                              use_32bit_registry=use_32bit_registry)

    if vdata == reg_current['vdata'] and reg_current['success']:
        ret['comment'] = '{0} in {1} is already configured' \
                         ''.format(salt.utils.stringutils.to_unicode(vname, 'utf-8') if vname else '(Default)',
                                   salt.utils.stringutils.to_unicode(name, 'utf-8'))
        return ret

    vdata_decoded = __utils__['reg.cast_vdata'](vdata=vdata, vtype=vtype)

    add_change = {'Key': r'{0}\{1}'.format(hive, key),
                  'Entry': '{0}'.format(salt.utils.stringutils.to_unicode(vname, 'utf-8') if vname else '(Default)'),
                  'Value': vdata_decoded}

    # Check for test option
    if __opts__['test']:
        ret['result'] = None
        ret['changes'] = {'reg': {'Will add': add_change}}
        return ret

    # Configure the value
    ret['result'] = __utils__['reg.set_value'](hive=hive,
                                               key=key,
                                               vname=vname,
                                               vdata=vdata,
                                               vtype=vtype,
                                               use_32bit_registry=use_32bit_registry)

    if not ret['result']:
        ret['changes'] = {}
        ret['comment'] = r'Failed to add {0} to {1}\{2}'.format(name, hive, key)
    else:
        ret['changes'] = {'reg': {'Added': add_change}}
        ret['comment'] = r'Added {0} to {1}\{2}'.format(name, hive, key)

    return ret