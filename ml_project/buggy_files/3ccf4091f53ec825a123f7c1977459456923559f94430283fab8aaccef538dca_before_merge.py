def _policyFileReplaceOrAppend(this_string, policy_data, append_only=False):
    '''
    helper function to take a ADMX policy string for registry.pol file data and
    update existing string or append the string to the data
    '''
    # we are going to clean off the special pre-fixes, so we get only the valuename
    if not policy_data:
        policy_data = ''
    specialValueRegex = r'(\*\*Del\.|\*\*DelVals\.){0,1}'
    item_key = None
    item_value_name = None
    data_to_replace = None
    if not append_only:
        item_key = this_string.split('{0};'.format(chr(0)))[0].lstrip('[')
        item_value_name = re.sub(specialValueRegex,
                                 '',
                                 this_string.split('{0};'.format(chr(0)))[1],
                                 flags=re.IGNORECASE)
        log.debug('item value name is {0}'.format(item_value_name))
        data_to_replace = _regexSearchKeyValueCombo(policy_data, item_key, item_value_name)
    if data_to_replace:
        log.debug('replacing {0} with {1}'.format([data_to_replace], [this_string]))
        policy_data = policy_data.replace(data_to_replace, this_string)
    else:
        log.debug('appending {0}'.format([this_string]))
        policy_data = ''.join([policy_data, this_string])

    return policy_data