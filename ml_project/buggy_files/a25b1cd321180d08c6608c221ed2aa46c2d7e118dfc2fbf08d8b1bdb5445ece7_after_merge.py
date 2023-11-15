def set_(computer_policy=None, user_policy=None,
         cumulative_rights_assignments=True,
         adml_language='en-US'):
    '''
    Set a local server policy.

    Args:

        computer_policy (dict):
            A dictionary of "policyname: value" pairs of computer policies to
            set. 'value' should be how it is displayed in the gpedit GUI, i.e.
            if a setting can be 'Enabled'/'Disabled', then that should be passed

            Administrative Template data may require dicts within dicts, to
            specify each element of the Administrative Template policy.
            Administrative Templates policies are always cumulative.

            Policy names can be specified in a number of ways based on the type
            of policy:

                Windows Settings Policies:

                    These policies can be specified using the GUI display name
                    or the key name from the _policy_info class in this module.
                    The GUI display name is also contained in the _policy_info
                    class in this module.

                Administrative Template Policies:

                    These can be specified using the policy name as displayed in
                    the GUI (case sensitive). Some policies have the same name,
                    but a different location (for example, "Access data sources
                    across domains"). These can be differentiated by the "path"
                    in the GUI (for example, "Windows Components\\Internet
                    Explorer\\Internet Control Panel\\Security Page\\Internet
                    Zone\\Access data sources across domains").

                    Additionally, policies can be specified using the "name" and
                    "id" attributes from the ADMX files.

                    For Administrative Templates that have policy elements, each
                    element can be specified using the text string as seen in
                    the GUI or using the ID attribute from the ADMX file. Due to
                    the way some of the GUI text is laid out, some policy
                    element names could include descriptive text that appears
                    lbefore the policy element in the GUI.

                    Use the get_policy_info function for the policy name to view
                    the element ID/names that the module will accept.

        user_policy (dict):
            The same setup as the computer_policy, except with data to configure
            the local user policy.

        cumulative_rights_assignments (bool):
            Determine how user rights assignment policies are configured.

            If True, user right assignment specifications are simply added to
            the existing policy

            If False, only the users specified will get the right (any existing
            will have the right revoked)

        adml_language (str):
            The language files to use for looking up Administrative Template
            policy data (i.e. how the policy is displayed in the GUI). Defaults
            to 'en-US' (U.S. English).

    Returns:
        bool: True is successful, otherwise False

    CLI Example:

    .. code-block:: bash

        salt '*' lgpo.set computer_policy="{'LockoutDuration': 2, 'RestrictAnonymous': 'Enabled', 'AuditProcessTracking': 'Succes, Failure'}"
    '''

    if computer_policy and not isinstance(computer_policy, dict):
        msg = 'computer_policy must be specified as a dict'
        raise SaltInvocationError(msg)
    if user_policy and not isinstance(user_policy, dict):
        msg = 'user_policy must be specified as a dict'
        raise SaltInvocationError(msg)
    policies = {}
    policies['User'] = user_policy
    policies['Machine'] = computer_policy
    if policies:
        for p_class in policies:
            _secedits = {}
            _modal_sets = {}
            _admTemplateData = {}
            _regedits = {}
            _lsarights = {}
            _policydata = _policy_info()
            admxPolicyDefinitions, admlPolicyResources = _processPolicyDefinitions(display_language=adml_language)
            if policies[p_class]:
                for policy_name in policies[p_class]:
                    _pol = None
                    policy_namespace = None
                    policy_key_name = policy_name
                    if policy_name in _policydata.policies[p_class]['policies']:
                        _pol = _policydata.policies[p_class]['policies'][policy_name]
                    else:
                        for policy in _policydata.policies[p_class]['policies']:
                            if _policydata.policies[p_class]['policies'][policy]['Policy'].upper() == \
                                    policy_name.upper():
                                _pol = _policydata.policies[p_class]['policies'][policy]
                                policy_key_name = policy
                    if _pol:
                        # transform and validate the setting
                        _value = _transformValue(policies[p_class][policy_name],
                                                 _policydata.policies[p_class]['policies'][policy_key_name],
                                                 'Put')
                        if not _validateSetting(_value, _policydata.policies[p_class]['policies'][policy_key_name]):
                            msg = 'The specified value {0} is not an acceptable setting for policy {1}.'
                            raise SaltInvocationError(msg.format(policies[p_class][policy_name], policy_name))
                        if 'Registry' in _pol:
                            # set value in registry
                            log.debug('{0} is a registry policy'.format(policy_name))
                            _regedits[policy_name] = {'policy': _pol, 'value': _value}
                        elif 'Secedit' in _pol:
                            # set value with secedit
                            log.debug('{0} is a Secedit policy'.format(policy_name))
                            if _pol['Secedit']['Section'] not in _secedits:
                                _secedits[_pol['Secedit']['Section']] = []
                            _secedits[_pol['Secedit']['Section']].append(
                                    ' '.join([_pol['Secedit']['Option'],
                                             '=', str(_value)]))
                        elif 'NetUserModal' in _pol:
                            # set value via NetUserModal
                            log.debug('{0} is a NetUserModal policy'.format(policy_name))
                            if _pol['NetUserModal']['Modal'] not in _modal_sets:
                                _modal_sets[_pol['NetUserModal']['Modal']] = {}
                            _modal_sets[_pol['NetUserModal']['Modal']][_pol['NetUserModal']['Option']] = _value
                        elif 'LsaRights' in _pol:
                            log.debug('{0} is a LsaRights policy'.format(policy_name))
                            _lsarights[policy_name] = {'policy': _pol, 'value': _value}
                    else:
                        _value = policies[p_class][policy_name]
                        log.debug('searching for "{0}" in admx data'.format(policy_name))
                        success, the_policy, policy_name_list, msg = _lookup_admin_template(
                                policy_name,
                                p_class,
                                adml_language=adml_language,
                                admx_policy_definitions=admxPolicyDefinitions,
                                adml_policy_resources=admlPolicyResources)
                        if success:
                            policy_name = the_policy.attrib['name']
                            policy_namespace = the_policy.nsmap[the_policy.prefix]
                            if policy_namespace not in _admTemplateData:
                                _admTemplateData[policy_namespace] = {}
                            _admTemplateData[policy_namespace][policy_name] = _value
                        else:
                            raise SaltInvocationError(msg)
                        if policy_namespace and policy_name in _admTemplateData[policy_namespace] and the_policy is not None:
                            log.debug('setting == {0}'.format(_admTemplateData[policy_namespace][policy_name]).lower())
                            log.debug('{0}'.format(str(_admTemplateData[policy_namespace][policy_name]).lower()))
                            if str(_admTemplateData[policy_namespace][policy_name]).lower() != 'disabled' \
                                    and str(_admTemplateData[policy_namespace][policy_name]).lower() != 'not configured':
                                if ELEMENTS_XPATH(the_policy):
                                    if isinstance(_admTemplateData[policy_namespace][policy_name], dict):
                                        for elements_item in ELEMENTS_XPATH(the_policy):
                                            for child_item in elements_item.getchildren():
                                                # check each element
                                                log.debug('checking element {0}'.format(child_item.attrib['id']))
                                                temp_element_name = None
                                                this_element_name = _getFullPolicyName(child_item,
                                                                                       child_item.attrib['id'],
                                                                                       True,
                                                                                       admlPolicyResources)
                                                log.debug('id attribute == "{0}"  this_element_name == "{1}"'.format(child_item.attrib['id'], this_element_name))
                                                if this_element_name in _admTemplateData[policy_namespace][policy_name]:
                                                    temp_element_name = this_element_name
                                                elif child_item.attrib['id'] in _admTemplateData[policy_namespace][policy_name]:
                                                    temp_element_name = child_item.attrib['id']
                                                else:
                                                    msg = ('Element "{0}" must be included'
                                                           ' in the policy configuration for policy {1}')
                                                    raise SaltInvocationError(msg.format(this_element_name, policy_name))
                                                if 'required' in child_item.attrib \
                                                        and child_item.attrib['required'].lower() == 'true':
                                                    if not _admTemplateData[policy_namespace][policy_name][temp_element_name]:
                                                        msg = 'Element "{0}" requires a value to be specified'
                                                        raise SaltInvocationError(msg.format(temp_element_name))
                                                if etree.QName(child_item).localname == 'boolean':
                                                    if not isinstance(
                                                            _admTemplateData[policy_namespace][policy_name][temp_element_name],
                                                            bool):
                                                        msg = 'Element {0} requires a boolean True or False'
                                                        raise SaltInvocationError(msg.format(temp_element_name))
                                                elif etree.QName(child_item).localname == 'decimal' or \
                                                        etree.QName(child_item).localname == 'longDecimal':
                                                    min_val = 0
                                                    max_val = 9999
                                                    if 'minValue' in child_item.attrib:
                                                        min_val = int(child_item.attrib['minValue'])
                                                    if 'maxValue' in child_item.attrib:
                                                        max_val = int(child_item.attrib['maxValue'])
                                                    if int(_admTemplateData[policy_namespace][policy_name][temp_element_name]) \
                                                            < min_val or \
                                                            int(_admTemplateData[policy_namespace][policy_name][temp_element_name]) \
                                                            > max_val:
                                                        msg = 'Element "{0}" value must be between {1} and {2}'
                                                        raise SaltInvocationError(msg.format(temp_element_name,
                                                                                             min_val,
                                                                                             max_val))
                                                elif etree.QName(child_item).localname == 'enum':
                                                    # make sure the value is in the enumeration
                                                    found = False
                                                    for enum_item in child_item.getchildren():
                                                        if _admTemplateData[policy_namespace][policy_name][temp_element_name] == \
                                                                _getAdmlDisplayName(
                                                                admlPolicyResources,
                                                                enum_item.attrib['displayName']).strip():
                                                            found = True
                                                            break
                                                    if not found:
                                                        msg = 'Element "{0}" does not have a valid value'
                                                        raise SaltInvocationError(msg.format(temp_element_name))
                                                elif etree.QName(child_item).localname == 'list':
                                                    if 'explicitValue' in child_item.attrib \
                                                                and child_item.attrib['explicitValue'].lower() == \
                                                                'true':
                                                        if not isinstance(
                                                                _admTemplateData[policy_namespace][policy_name][temp_element_name],
                                                                dict):
                                                            msg = ('Each list item of element "{0}" '
                                                                   'requires a dict value')
                                                            msg = msg.format(temp_element_name)
                                                            raise SaltInvocationError(msg)
                                                    elif not isinstance(
                                                            _admTemplateData[policy_namespace][policy_name][temp_element_name],
                                                            list):
                                                        msg = 'Element "{0}" requires a list value'
                                                        msg = msg.format(temp_element_name)
                                                        raise SaltInvocationError(msg)
                                                elif etree.QName(child_item).localname == 'multiText':
                                                    if not isinstance(
                                                            _admTemplateData[policy_namespace][policy_name][temp_element_name],
                                                            list):
                                                        msg = 'Element "{0}" requires a list value'
                                                        msg = msg.format(temp_element_name)
                                                        raise SaltInvocationError(msg)
                                                _admTemplateData[policy_namespace][policy_name][child_item.attrib['id']] = \
                                                    _admTemplateData[policy_namespace][policy_name].pop(temp_element_name)
                                    else:
                                        msg = 'The policy "{0}" has elements which must be configured'
                                        msg = msg.format(policy_name)
                                        raise SaltInvocationError(msg)
                                else:
                                    if str(_admTemplateData[policy_namespace][policy_name]).lower() != 'enabled':
                                        msg = ('The policy {0} must either be "Enabled", '
                                               '"Disabled", or "Not Configured"')
                                        msg = msg.format(policy_name)
                                        raise SaltInvocationError(msg)
                if _regedits:
                    for regedit in _regedits:
                        log.debug('{0} is a Registry policy'.format(regedit))
                        # if the value setting is None or "(value not set)", we will delete the value from the registry
                        if _regedits[regedit]['value'] is not None and _regedits[regedit]['value'] != '(value not set)':
                            _ret = __salt__['reg.set_value'](
                                    _regedits[regedit]['policy']['Registry']['Hive'],
                                    _regedits[regedit]['policy']['Registry']['Path'],
                                    _regedits[regedit]['policy']['Registry']['Value'],
                                    _regedits[regedit]['value'],
                                    _regedits[regedit]['policy']['Registry']['Type'])
                        else:
                            _ret = __salt__['reg.delete_value'](
                                    _regedits[regedit]['policy']['Registry']['Hive'],
                                    _regedits[regedit]['policy']['Registry']['Path'],
                                    _regedits[regedit]['policy']['Registry']['Value'])
                        if not _ret:
                            msg = ('Error while attempting to set policy {0} via the registry.'
                                   '  Some changes may not be applied as expected')
                            raise CommandExecutionError(msg.format(regedit))
                if _lsarights:
                    for lsaright in _lsarights:
                        _existingUsers = None
                        if not cumulative_rights_assignments:
                            _existingUsers = _getRightsAssignments(
                                    _lsarights[lsaright]['policy']['LsaRights']['Option'])
                        if _lsarights[lsaright]['value']:
                            for acct in _lsarights[lsaright]['value']:
                                _ret = _addAccountRights(acct, _lsarights[lsaright]['policy']['LsaRights']['Option'])
                                if not _ret:
                                    msg = 'An error occurred attempting to configure the user right {0}.'
                                    raise SaltInvocationError(msg.format(lsaright))
                        if _existingUsers:
                            for acct in _existingUsers:
                                if acct not in _lsarights[lsaright]['value']:
                                    _ret = _delAccountRights(
                                            acct, _lsarights[lsaright]['policy']['LsaRights']['Option'])
                                    if not _ret:
                                        msg = ('An error occurred attempting to remove previously'
                                               'configured users with right {0}.')
                                        raise SaltInvocationError(msg.format(lsaright))
                if _secedits:
                    # we've got secedits to make
                    log.debug(_secedits)
                    _iniData = '\r\n'.join(['[Unicode]', 'Unicode=yes'])
                    _seceditSections = ['System Access', 'Event Audit', 'Registry Values', 'Privilege Rights']
                    for _seceditSection in _seceditSections:
                        if _seceditSection in _secedits:
                            _iniData = '\r\n'.join([_iniData, ''.join(['[', _seceditSection, ']']),
                                                   '\r\n'.join(_secedits[_seceditSection])])
                    _iniData = '\r\n'.join([_iniData, '[Version]', 'signature="$CHICAGO$"', 'Revision=1'])
                    log.debug('_iniData == {0}'.format(_iniData))
                    _ret = _importSeceditConfig(_iniData)
                    if not _ret:
                        msg = ('Error while attempting to set policies via secedit.'
                               '  Some changes may not be applied as expected')
                        raise CommandExecutionError(msg)
                if _modal_sets:
                    # we've got modalsets to make
                    log.debug(_modal_sets)
                    for _modal_set in _modal_sets:
                        try:
                            _existingModalData = win32net.NetUserModalsGet(None, _modal_set)
                            _newModalSetData = dictupdate.update(_existingModalData, _modal_sets[_modal_set])
                            log.debug('NEW MODAL SET = {0}'.format(_newModalSetData))
                            _ret = win32net.NetUserModalsSet(None, _modal_set, _newModalSetData)
                        except:
                            msg = 'An unhandled exception occurred while attempting to set policy via NetUserModalSet'
                            raise CommandExecutionError(msg)
                if _admTemplateData:
                    _ret = False
                    log.debug('going to write some adm template data :: {0}'.format(_admTemplateData))
                    _ret = _writeAdminTemplateRegPolFile(_admTemplateData,
                                                         admxPolicyDefinitions,
                                                         admlPolicyResources,
                                                         registry_class=p_class)
                    if not _ret:
                        msg = ('Error while attempting to write Administrative Template Policy data.'
                               '  Some changes may not be applied as expected')
                        raise CommandExecutionError(msg)
        return True
    else:
        msg = 'You have to specify something!'
        raise SaltInvocationError(msg)