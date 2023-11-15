def _regexSearchKeyValueCombo(policy_data, policy_regpath, policy_regkey):
    '''
    helper function to do a search of Policy data from a registry.pol file
    for a policy_regpath and policy_regkey combo
    '''
    if policy_data:
        specialValueRegex = salt.utils.to_bytes(r'(\*\*Del\.|\*\*DelVals\.){0,1}')
        _thisSearch = b''.join([salt.utils.to_bytes(r'\['),
                               re.escape(policy_regpath),
                               b'\00;',
                               specialValueRegex,
                               re.escape(policy_regkey),
                               b'\00;'])
        match = re.search(_thisSearch, policy_data, re.IGNORECASE)
        if match:
            return policy_data[match.start():(policy_data.index(']', match.end())) + 1]

    return None