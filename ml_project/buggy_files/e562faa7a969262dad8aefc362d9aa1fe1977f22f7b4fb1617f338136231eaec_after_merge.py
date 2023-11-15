def _policyFileReplaceOrAppendList(string_list, policy_data):
    '''
    helper function to take a list of strings for registry.pol file data and
    update existing strings or append the strings
    '''
    if not policy_data:
        policy_data = b''
    # we are going to clean off the special pre-fixes, so we get only the valuename
    specialValueRegex = salt.utils.to_bytes(r'(\*\*Del\.|\*\*DelVals\.){0,1}')
    for this_string in string_list:
        list_item_key = this_string.split(b'\00;')[0].lstrip(b'[')
        list_item_value_name = re.sub(specialValueRegex,
                                      b'',
                                      this_string.split(b'\00;')[1],
                                      flags=re.IGNORECASE)
        log.debug('item value name is {0}'.format(list_item_value_name))
        data_to_replace = _regexSearchKeyValueCombo(policy_data,
                                                    list_item_key,
                                                    list_item_value_name)
        if data_to_replace:
            log.debug('replacing {0} with {1}'.format([data_to_replace], [this_string]))
            policy_data = policy_data.replace(data_to_replace, this_string)
        else:
            log.debug('appending {0}'.format([this_string]))
            policy_data = b''.join([policy_data, this_string])
    return policy_data