def _getDataFromRegPolData(search_string, policy_data, return_value_name=False):
    '''
    helper function to do a search of Policy data from a registry.pol file
    returns the "data" field
    https://msdn.microsoft.com/en-us/library/aa374407(VS.85).aspx
    [key;value;type;size;data]
    '''
    value = None
    values = []
    encoded_semicolon = ';'.encode('utf-16-le')
    if return_value_name:
        values = {}
    if search_string:
        registry = Registry()
        if len(search_string.split(encoded_semicolon)) >= 3:
            vtype = registry.vtype_reverse[ord(search_string.split(encoded_semicolon)[2].decode('utf-32-le'))]
        else:
            vtype = None
        search_string = re.escape(search_string)
        matches = re.finditer(search_string, policy_data, re.IGNORECASE)
        matches = [m for m in matches]
        if matches:
            for match in matches:
                pol_entry = policy_data[match.start():(policy_data.index(']'.encode('utf-16-le'),
                                                                         match.end())
                                                       )
                                        ].split(encoded_semicolon)
                if len(pol_entry) >= 2:
                    valueName = pol_entry[1]
                if len(pol_entry) >= 5:
                    value = pol_entry[4]
                    if vtype == 'REG_DWORD' or vtype == 'REG_QWORD':
                        if value:
                            if vtype == 'REG_DWORD':
                                for v in struct.unpack('I', value):
                                    value = v
                            elif vtype == 'REG_QWORD':
                                for v in struct.unpack('Q', value):
                                    value = v
                        else:
                            value = 0
                    elif vtype == 'REG_MULTI_SZ':
                        value = value.decode('utf-16-le').rstrip(chr(0)).split(chr(0))
                    else:
                        value = value.decode('utf-16-le').rstrip(chr(0))
                if return_value_name:
                    log.debug('we want value names and the value')
                    values[valueName] = value
                elif len(matches) > 1:
                    log.debug('we have multiple matches, we will return a list')
                    values.append(value)
    if values:
        value = values

    return value