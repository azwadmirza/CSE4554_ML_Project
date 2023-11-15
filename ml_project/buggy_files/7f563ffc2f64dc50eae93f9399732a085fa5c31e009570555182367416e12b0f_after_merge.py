def _buildKnownDataSearchString(reg_key, reg_valueName, reg_vtype, reg_data,
                                check_deleted=False):
    '''
    helper function similar to _processValueItem to build a search string for a
    known key/value/type/data
    '''
    registry = Registry()
    this_element_value = None
    expected_string = b''
    encoded_semicolon = ';'.encode('utf-16-le')
    encoded_null = chr(0).encode('utf-16-le')
    if reg_key:
        reg_key = reg_key.encode('utf-16-le')
    if reg_valueName:
        reg_valueName = reg_valueName.encode('utf-16-le')
    if reg_data and not check_deleted:
        if reg_vtype == 'REG_DWORD':
            this_element_value = struct.pack('I', int(reg_data))
        elif reg_vtype == "REG_QWORD":
            this_element_value = struct.pack('Q', int(reg_data))
        elif reg_vtype == 'REG_SZ':
            this_element_value = b''.join([reg_data.encode('utf-16-le'),
                                           encoded_null])
    if check_deleted:
        reg_vtype = 'REG_SZ'
        expected_string = b''.join(['['.encode('utf-16-le'),
                                    reg_key,
                                    encoded_null,
                                    encoded_semicolon,
                                    '**del.'.encode('utf-16-le'),
                                    reg_valueName,
                                    encoded_null,
                                    encoded_semicolon,
                                    chr(registry.vtype[reg_vtype]).encode('utf-32-le'),
                                    encoded_semicolon,
                                    unichr(len(' {0}'.format(chr(0)).encode('utf-16-le'))).encode('utf-32-le'),
                                    encoded_semicolon,
                                    ' '.encode('utf-16-le'),
                                    encoded_null,
                                    ']'.encode('utf-16-le')])
    else:
        expected_string = b''.join(['['.encode('utf-16-le'),
                                    reg_key,
                                    encoded_null,
                                    encoded_semicolon,
                                    reg_valueName,
                                    encoded_null,
                                    encoded_semicolon,
                                    chr(registry.vtype[reg_vtype]).encode('utf-32-le'),
                                    encoded_semicolon,
                                    unichr(len(this_element_value)).encode('utf-32-le'),
                                    encoded_semicolon,
                                    this_element_value,
                                    ']'.encode('utf-16-le')])
    return expected_string