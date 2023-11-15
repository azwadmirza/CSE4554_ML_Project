def _buildKnownDataSearchString(reg_key, reg_valueName, reg_vtype, reg_data,
                                check_deleted=False):
    '''
    helper function similar to _processValueItem to build a search string for a
    known key/value/type/data
    '''
    registry = Registry()
    this_element_value = None
    expected_string = ''
    if reg_data and not check_deleted:
        if reg_vtype == 'REG_DWORD':
            this_element_value = ''
            for v in struct.unpack('2H', struct.pack('I', int(reg_data))):
                this_element_value = this_element_value + unichr(v)
        elif reg_vtype == 'REG_QWORD':
            this_element_value = ''
            for v in struct.unpack('4H', struct.pack('I', int(reg_data))):
                this_element_value = this_element_value + unichr(v)
        elif reg_vtype == 'REG_SZ':
            this_element_value = '{0}{1}'.format(reg_data, chr(0))
    if check_deleted:
        reg_vtype = 'REG_SZ'
        expected_string = u'[{1}{0};**del.{2}{0};{3}{0};{4}{0};{5}{0}]'.format(
                                chr(0),
                                reg_key,
                                reg_valueName,
                                chr(registry.vtype[reg_vtype]),
                                unichr(len(' {0}'.format(chr(0)).encode('utf-16-le'))),
                                ' ')
    else:
        expected_string = u'[{1}{0};{2}{0};{3}{0};{4}{0};{5}]'.format(
                                chr(0),
                                reg_key,
                                reg_valueName,
                                chr(registry.vtype[reg_vtype]),
                                unichr(len(this_element_value.encode('utf-16-le'))),
                                this_element_value)
    return expected_string