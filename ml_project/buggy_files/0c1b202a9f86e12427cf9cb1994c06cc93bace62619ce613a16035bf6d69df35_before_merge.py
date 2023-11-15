def _processValueItem(element, reg_key, reg_valuename, policy, parent_element,
                      check_deleted=False, this_element_value=None):
    '''
    helper function to process a value type item and generate the expected
    string in the Registry.pol file

    element - the element to process
    reg_key - the registry key associated with the element (some inherit from
              their parent policy)
    reg_valuename - the registry valueName associated with the element (some
                    inherit from their parent policy)
    policy - the parent policy element
    parent_element - the parent element (primarily passed in to differentiate
                     children of "elements" objects
    check_deleted - if the returned expected string should be for a deleted
                    value
    this_element_value - a specific value to place into the expected string
                         returned for "elements" children whose values are
                         specified by the user
    '''
    registry = Registry()
    expected_string = None
    # https://msdn.microsoft.com/en-us/library/dn606006(v=vs.85).aspx
    this_vtype = 'REG_SZ'
    encoded_semicolon = ';'.encode('utf-16-le')
    encoded_null = chr(0).encode('utf-16-le')
    if reg_key:
        reg_key = reg_key.encode('utf-16-le')
    if reg_valuename:
        reg_valuename = reg_valuename.encode('utf-16-le')
    if etree.QName(element).localname == 'decimal' and etree.QName(parent_element).localname != 'elements':
        this_vtype = 'REG_DWORD'
        if 'value' in element.attrib:
            this_element_value = struct.pack(b'I', int(element.attrib['value']))
        else:
            log.error('The %s child %s element for the policy with '
                      'attributes: %s does not have the required "value" '
                      'attribute. The element attributes are: %s',
                      etree.QName(parent_element).localname,
                      etree.QName(element).localname,
                      policy.attrib,
                      element.attrib)
            return None
    elif etree.QName(element).localname == 'longDecimal' and etree.QName(parent_element).localname != 'elements':
        # WARNING: no longDecimals in current ADMX files included with 2012
        # server, so untested/assumed
        this_vtype = 'REG_QWORD'
        if 'value' in element.attrib:
            this_element_value = struct.pack(b'Q', int(element.attrib['value']))
        else:
            log.error('The %s child %s element for the policy with '
                      'attributes: %s does not have the required "value" '
                      'attribute. The element attributes are: %s',
                      etree.QName(parent_element).localname,
                      etree.QName(element).localname,
                      policy.attrib,
                      element.attrib)
            return None
    elif etree.QName(element).localname == 'string':
        this_vtype = 'REG_SZ'
        this_element_value = b''.join([element.text.encode('utf-16-le'),
                                       encoded_null])
    elif etree.QName(parent_element).localname == 'elements':
        standard_element_expected_string = True
        if etree.QName(element).localname == 'boolean':
            # a boolean element that has no children will add a REG_DWORD == 1
            # on true or delete the value on false
            # https://msdn.microsoft.com/en-us/library/dn605978(v=vs.85).aspx
            if this_element_value is False:
                check_deleted = True
            if not check_deleted:
                this_vtype = 'REG_DWORD'
            this_element_value = chr(1).encode('utf-16-le')
            standard_element_expected_string = False
        elif etree.QName(element).localname == 'decimal':
            # https://msdn.microsoft.com/en-us/library/dn605987(v=vs.85).aspx
            this_vtype = 'REG_DWORD'
            requested_val = this_element_value
            if this_element_value is not None:
                this_element_value = struct.pack(b'I', int(this_element_value))
            if 'storeAsText' in element.attrib:
                if element.attrib['storeAsText'].lower() == 'true':
                    this_vtype = 'REG_SZ'
                    if requested_val is not None:
                        this_element_value = six.text_type(requested_val).encode('utf-16-le')
            if check_deleted:
                this_vtype = 'REG_SZ'
        elif etree.QName(element).localname == 'longDecimal':
            # https://msdn.microsoft.com/en-us/library/dn606015(v=vs.85).aspx
            this_vtype = 'REG_QWORD'
            requested_val = this_element_value
            if this_element_value is not None:
                this_element_value = struct.pack(b'Q', int(this_element_value))
            if 'storeAsText' in element.attrib:
                if element.attrib['storeAsText'].lower() == 'true':
                    this_vtype = 'REG_SZ'
                    if requested_val is not None:
                        this_element_value = six.text_type(requested_val).encode('utf-16-le')
        elif etree.QName(element).localname == 'text':
            # https://msdn.microsoft.com/en-us/library/dn605969(v=vs.85).aspx
            this_vtype = 'REG_SZ'
            if 'expandable' in element.attrib:
                if element.attrib['expandable'].lower() == 'true':
                    this_vtype = 'REG_EXPAND_SZ'
            if this_element_value is not None:
                this_element_value = b''.join([this_element_value.encode('utf-16-le'),
                                               encoded_null])
        elif etree.QName(element).localname == 'multiText':
            this_vtype = 'REG_MULTI_SZ' if not check_deleted else 'REG_SZ'
            if this_element_value is not None:
                this_element_value = '{0}{1}{1}'.format(chr(0).join(this_element_value), chr(0))
        elif etree.QName(element).localname == 'list':
            standard_element_expected_string = False
            del_keys = b''
            element_valuenames = []
            element_values = this_element_value
            if this_element_value is not None:
                element_valuenames = list([str(z) for z in range(1, len(this_element_value) + 1)])
            if 'additive' in element.attrib:
                if element.attrib['additive'].lower() == 'false':
                    # a delete values will be added before all the other
                    # value = data pairs
                    del_keys = b''.join(['['.encode('utf-16-le'),
                                         reg_key,
                                         encoded_null,
                                         encoded_semicolon,
                                         '**delvals.'.encode('utf-16-le'),
                                         encoded_null,
                                         encoded_semicolon,
                                         chr(registry.vtype[this_vtype]).encode('utf-32-le'),
                                         encoded_semicolon,
                                         six.unichr(len(' {0}'.format(chr(0)).encode('utf-16-le'))).encode('utf-32-le'),
                                         encoded_semicolon,
                                         ' '.encode('utf-16-le'),
                                         encoded_null,
                                         ']'.encode('utf-16-le')])
            if 'expandable' in element.attrib:
                this_vtype = 'REG_EXPAND_SZ'
            if 'explicitValue' in element.attrib and element.attrib['explicitValue'].lower() == 'true':
                if this_element_value is not None:
                    element_valuenames = this_element_value.keys()
                    element_values = this_element_value.values()
            if 'valuePrefix' in element.attrib:
                # if the valuePrefix attribute exists, the valuenames are <prefix><number>
                # most prefixes attributes are empty in the admx files, so the valuenames
                # end up being just numbers
                if element.attrib['valuePrefix'] != '':
                    if this_element_value is not None:
                        element_valuenames = ['{0}{1}'.format(element.attrib['valuePrefix'],
                                                              k) for k in element_valuenames]
            else:
                # if there is no valuePrefix attribute, the valuename is the value
                if element_values is not None:
                    element_valuenames = [str(z) for z in element_values]
            if not check_deleted:
                if this_element_value is not None:
                    log.debug('_processValueItem has an explicit '
                              'element_value of %s', this_element_value)
                    expected_string = del_keys
                    log.debug('element_valuenames == %s and element_values '
                              '== %s', element_valuenames, element_values)
                    for i, item in enumerate(element_valuenames):
                        expected_string = expected_string + b''.join(['['.encode('utf-16-le'),
                                                                      reg_key,
                                                                      encoded_null,
                                                                      encoded_semicolon,
                                                                      element_valuenames[i].encode('utf-16-le'),
                                                                      encoded_null,
                                                                      encoded_semicolon,
                                                                      chr(registry.vtype[this_vtype]).encode('utf-32-le'),
                                                                      encoded_semicolon,
                                                                      six.unichr(len('{0}{1}'.format(element_values[i],
                                                                                 chr(0)).encode('utf-16-le'))).encode('utf-32-le'),
                                                                      encoded_semicolon,
                                                                      b''.join([element_values[i].encode('utf-16-le'),
                                                                               encoded_null]),
                                                                      ']'.encode('utf-16-le')])
                else:
                    expected_string = del_keys + b''.join(['['.encode('utf-16-le'),
                                                           reg_key,
                                                           encoded_null,
                                                           encoded_semicolon])
            else:
                expected_string = b''.join(['['.encode('utf-16-le'),
                                            reg_key,
                                            encoded_null,
                                            encoded_semicolon,
                                            '**delvals.'.encode('utf-16-le'),
                                            encoded_null,
                                            encoded_semicolon,
                                            chr(registry.vtype[this_vtype]).encode('utf-32-le'),
                                            encoded_semicolon,
                                            six.unichr(len(' {0}'.format(chr(0)).encode('utf-16-le'))).encode('utf-32-le'),
                                            encoded_semicolon,
                                            ' '.encode('utf-16-le'),
                                            encoded_null,
                                            ']'.encode('utf-16-le')])
        elif etree.QName(element).localname == 'enum':
            if this_element_value is not None:
                pass

        if standard_element_expected_string and not check_deleted:
            if this_element_value is not None:
                expected_string = b''.join(['['.encode('utf-16-le'),
                                            reg_key,
                                            encoded_null,
                                            encoded_semicolon,
                                            reg_valuename,
                                            encoded_null,
                                            encoded_semicolon,
                                            chr(registry.vtype[this_vtype]).encode('utf-32-le'),
                                            encoded_semicolon,
                                            six.unichr(len(this_element_value)).encode('utf-32-le'),
                                            encoded_semicolon,
                                            this_element_value,
                                            ']'.encode('utf-16-le')])
            else:
                expected_string = b''.join(['['.encode('utf-16-le'),
                                            reg_key,
                                            encoded_null,
                                            encoded_semicolon,
                                            reg_valuename,
                                            encoded_null,
                                            encoded_semicolon,
                                            chr(registry.vtype[this_vtype]).encode('utf-32-le'),
                                            encoded_semicolon])

    if not expected_string:
        if etree.QName(element).localname == "delete" or check_deleted:
            # delete value
            expected_string = b''.join(['['.encode('utf-16-le'),
                                        reg_key,
                                        encoded_null,
                                        encoded_semicolon,
                                        '**del.'.encode('utf-16-le'),
                                        reg_valuename,
                                        encoded_null,
                                        encoded_semicolon,
                                        chr(registry.vtype[this_vtype]).encode('utf-32-le'),
                                        encoded_semicolon,
                                        six.unichr(len(' {0}'.format(chr(0)).encode('utf-16-le'))).encode('utf-32-le'),
                                        encoded_semicolon,
                                        ' '.encode('utf-16-le'),
                                        encoded_null,
                                        ']'.encode('utf-16-le')])
        else:
            expected_string = b''.join(['['.encode('utf-16-le'),
                                        reg_key,
                                        encoded_null,
                                        encoded_semicolon,
                                        reg_valuename,
                                        encoded_null,
                                        encoded_semicolon,
                                        chr(registry.vtype[this_vtype]).encode('utf-32-le'),
                                        encoded_semicolon,
                                        six.unichr(len(this_element_value)).encode('utf-32-le'),
                                        encoded_semicolon,
                                        this_element_value,
                                        ']'.encode('utf-16-le')])
    return expected_string