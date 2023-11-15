def _regexSearchKeyValueCombo(policy_data, policy_regpath, policy_regkey):
    '''
    helper function to do a search of Policy data from a registry.pol file
    for a policy_regpath and policy_regkey combo
    '''
    if policy_data:
        specialValueRegex = r'(\*\*Del\.|\*\*DelVals\.){0,1}'
        _thisSearch = r'\[{1}{0};{3}{2}{0};'.format(
                chr(0),
                re.escape(policy_regpath),
                re.escape(policy_regkey),
                specialValueRegex)
        match = re.search(_thisSearch, policy_data, re.IGNORECASE)
        if match:
            return policy_data[match.start():(policy_data.index(']', match.end())) + 1]

    return None