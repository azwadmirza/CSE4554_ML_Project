def _getDataFromRegPolData(search_string, policy_data, return_value_name=False):
    '''
    helper function to do a search of Policy data from a registry.pol file
    returns the "data" field
    https://msdn.microsoft.com/en-us/library/aa374407(VS.85).aspx
    [key;value;type;size;data]
    '''
    value = None
    values = []
    if return_value_name:
        values = {}
    if search_string:
        registry = Registry()
        if len(search_string.split('{0};'.format(chr(0)))) >= 3:
            vtype = registry.vtype_reverse[ord(search_string.split('{0};'.format(chr(0)))[2])]
        else:
            vtype = None
        search_string = re.escape(search_string)
        matches = re.finditer(search_string, policy_data, re.IGNORECASE)
        matches = [m for m in matches]
        if matches:
            for match in matches:
                pol_entry = policy_data[match.start():(policy_data.index(']',
                                                                         match.end())
                                                       )
                                        ].split('{0};'.format(chr(0)))
                if len(pol_entry) >= 2:
                    valueName = pol_entry[1]
                if len(pol_entry) >= 5:
                    value = pol_entry[4]
                    if vtype == 'REG_DWORD' or vtype == 'REG_QWORD':
                        if value:
                            vlist = list(ord(v) for v in value)
                            if vtype == 'REG_DWORD':
                                for v in struct.unpack('I', struct.pack('2H', *vlist)):
                                    value = v
                            elif vtype == 'REG_QWORD':
                                for v in struct.unpack('I', struct.pack('4H', *vlist)):
                                    value = v
                        else:
                            value = 0
                    elif vtype == 'REG_MULTI_SZ':
                        value = value.rstrip(chr(0)).split(chr(0))
                    else:
                        value = value.rstrip(chr(0))
                if return_value_name:
                    log.debug('we want value names and the value')
                    values[valueName] = value
                elif len(matches) > 1:
                    log.debug('we have multiple matches, we will return a list')
                    values.append(value)
    if values:
        value = values

    return value