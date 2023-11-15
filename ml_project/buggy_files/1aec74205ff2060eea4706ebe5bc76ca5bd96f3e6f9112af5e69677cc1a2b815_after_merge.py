def get_policy_info(policy_name,
                    policy_class,
                    adml_language='en-US'):
    '''
    Returns information about a specified policy

    Args:
        policy_name (str):
            The name of the policy to lookup
        policy_class (str):
            The class of policy, i.e. machine, user, both
        adml_language (str):
            The ADML language to use for Administrative Template data lookup

    Returns:
        dict: Information about the specified policy

    CLI Example:

    .. code-block:: bash

        salt '*' lgpo.get_policy_info 'Maximum password age' machine
    '''
    # return the possible policy names and element names
    ret = {'policy_name': policy_name,
           'policy_class': policy_class,
           'policy_aliases': [],
           'policy_found': False,
           'rights_assignment': False,
           'policy_elements': [],
           'message': 'policy not found'}
    policy_class = policy_class.title()
    policy_data = _policy_info()
    admx_policy_definitions, adml_policy_resources = _processPolicyDefinitions(
            display_language=adml_language)
    if policy_class not in policy_data.policies.keys():
        ret['message'] = 'The requested policy class "{0}" is invalid, policy_class should be one of: {1}'.format(
                policy_class,
                ', '.join(policy_data.policies.keys()))
        return ret
    if policy_name in policy_data.policies[policy_class]['policies']:
        ret['policy_aliases'].append(policy_data.policies[policy_class]['policies'][policy_name]['Policy'])
        ret['policy_found'] = True
        ret['message'] = ''
        if 'LsaRights' in policy_data.policies[policy_class]['policies'][policy_name]:
            ret['rights_assignment'] = True
        return ret
    else:
        for pol in policy_data.policies[policy_class]['policies'].keys():
            if policy_data.policies[policy_class]['policies'][pol]['Policy'].lower() == policy_name.lower():
                ret['policy_aliases'].append(pol)
                ret['policy_found'] = True
                ret['message'] = ''
                if 'LsaRights' in policy_data.policies[policy_class]['policies'][pol]:
                    ret['rights_assignment'] = True
                return ret
    success, policy_xml_item, policy_name_list, message = _lookup_admin_template(
            policy_name,
            policy_class,
            adml_language=adml_language,
            admx_policy_definitions=admx_policy_definitions,
            adml_policy_resources=adml_policy_resources)
    if success:
        for elements_item in ELEMENTS_XPATH(policy_xml_item):
            for child_item in elements_item.getchildren():
                this_element_name = _getFullPolicyName(child_item,
                                                       child_item.attrib['id'],
                                                       True,
                                                       adml_policy_resources)
                ret['policy_elements'].append(
                        {'element_id': child_item.attrib['id'],
                         'element_aliases': [child_item.attrib['id'], this_element_name]})
        ret['policy_aliases'] = policy_name_list
        ret['policy_found'] = True
        ret['message'] = ''
        return ret
    else:
        ret['message'] = message

    return ret