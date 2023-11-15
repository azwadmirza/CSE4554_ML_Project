def _checkAllAdmxPolicies(policy_class,
                          admx_policy_definitions,
                          adml_policy_resources,
                          return_full_policy_names=False,
                          hierarchical_return=False,
                          return_not_configured=False):
    '''
    rewrite of _getAllAdminTemplateSettingsFromRegPolFile where instead of
    looking only at the contents of the file, we're going to loop through every
    policy and look in the registry.pol file to determine if it is
    enabled/disabled/not configured
    '''
    log.debug('POLICY CLASS == {0}'.format(policy_class))
    module_policy_data = _policy_info()
    policy_filedata = _read_regpol_file(module_policy_data.admx_registry_classes[policy_class]['policy_path'])
    admx_policies = []
    policy_vals = {}
    hierarchy = {}
    full_names = {}
    if policy_filedata:
        log.debug('POLICY CLASS {0} has file data'.format(policy_class))
        policy_filedata_split = re.sub(salt.utils.to_bytes(r'\]{0}$'.format(chr(0))),
                                       b'',
                                       re.sub(salt.utils.to_bytes(r'^\[{0}'.format(chr(0))),
                                              b'',
                                              re.sub(re.escape(module_policy_data.reg_pol_header.encode('utf-16-le')), b'', policy_filedata))
                                       ).split(']['.encode('utf-16-le'))
        for policy_item in policy_filedata_split:
            policy_item_key = policy_item.split('{0};'.format(chr(0)).encode('utf-16-le'))[0].decode('utf-16-le').lower()
            if policy_item_key:
                for admx_item in REGKEY_XPATH(admx_policy_definitions, keyvalue=policy_item_key):
                    if etree.QName(admx_item).localname == 'policy':
                        if admx_item not in admx_policies:
                            admx_policies.append(admx_item)
                    else:
                        for policy_item in POLICY_ANCESTOR_XPATH(admx_item):
                            if policy_item not in admx_policies:
                                admx_policies.append(policy_item)

        log.debug('{0} policies to examine'.format(len(admx_policies)))
        if return_not_configured:
            log.debug('returning non configured policies')
            not_configured_policies = ALL_CLASS_POLICY_XPATH(admx_policy_definitions, registry_class=policy_class)
            for policy_item in admx_policies:
                if policy_item in not_configured_policies:
                    not_configured_policies.remove(policy_item)

            for not_configured_policy in not_configured_policies:
                not_configured_policy_namespace = not_configured_policy.nsmap[not_configured_policy.prefix]
                if not_configured_policy_namespace not in policy_vals:
                    policy_vals[not_configured_policy_namespace] = {}
                policy_vals[not_configured_policy_namespace][not_configured_policy.attrib['name']] = 'Not Configured'
                if return_full_policy_names:
                    if not_configured_policy_namespace not in full_names:
                        full_names[not_configured_policy_namespace] = {}
                    full_names[not_configured_policy_namespace][not_configured_policy.attrib['name']] = _getFullPolicyName(
                            not_configured_policy,
                            not_configured_policy.attrib['name'],
                            return_full_policy_names,
                            adml_policy_resources)
                log.debug('building hierarchy for non-configured item {0}'.format(not_configured_policy.attrib['name']))
                if not_configured_policy_namespace not in hierarchy:
                    hierarchy[not_configured_policy_namespace] = {}
                hierarchy[not_configured_policy_namespace][not_configured_policy.attrib['name']] = _build_parent_list(
                        not_configured_policy,
                        admx_policy_definitions,
                        return_full_policy_names,
                        adml_policy_resources)
        for admx_policy in admx_policies:
            this_key = None
            this_valuename = None
            this_policyname = None
            this_policynamespace = None
            this_policy_setting = 'Not Configured'
            element_only_enabled_disabled = True
            explicit_enable_disable_value_setting = False

            if 'key' in admx_policy.attrib:
                this_key = admx_policy.attrib['key']
            else:
                log.error('policy item {0} does not have the required "key" '
                          'attribute'.format(admx_policy.attrib))
                break
            if 'valueName' in admx_policy.attrib:
                this_valuename = admx_policy.attrib['valueName']
            if 'name' in admx_policy.attrib:
                this_policyname = admx_policy.attrib['name']
            else:
                log.error('policy item {0} does not have the required "name" '
                          'attribute'.format(admx_policy.attrib))
                break
            this_policynamespace = admx_policy.nsmap[admx_policy.prefix]
            if ENABLED_VALUE_XPATH(admx_policy) and this_policy_setting == 'Not Configured':
                # some policies have a disabled list but not an enabled list
                # added this to address those issues
                if DISABLED_LIST_XPATH(admx_policy):
                    element_only_enabled_disabled = False
                    explicit_enable_disable_value_setting = True
                if _checkValueItemParent(admx_policy,
                                         this_policyname,
                                         this_key,
                                         this_valuename,
                                         ENABLED_VALUE_XPATH,
                                         policy_filedata):
                    this_policy_setting = 'Enabled'
                    log.debug('{0} is enabled'.format(this_policyname))
                    if this_policynamespace not in policy_vals:
                        policy_vals[this_policynamespace] = {}
                    policy_vals[this_policynamespace][this_policyname] = this_policy_setting
            if DISABLED_VALUE_XPATH(admx_policy) and this_policy_setting == 'Not Configured':
                # some policies have a disabled list but not an enabled list
                # added this to address those issues
                if ENABLED_LIST_XPATH(admx_policy):
                    element_only_enabled_disabled = False
                    explicit_enable_disable_value_setting = True
                if _checkValueItemParent(admx_policy,
                                         this_policyname,
                                         this_key,
                                         this_valuename,
                                         DISABLED_VALUE_XPATH,
                                         policy_filedata):
                    this_policy_setting = 'Disabled'
                    log.debug('{0} is disabled'.format(this_policyname))
                    if this_policynamespace not in policy_vals:
                        policy_vals[this_policynamespace] = {}
                    policy_vals[this_policynamespace][this_policyname] = this_policy_setting
            if ENABLED_LIST_XPATH(admx_policy) and this_policy_setting == 'Not Configured':
                element_only_enabled_disabled = False
                explicit_enable_disable_value_setting = True
                if _checkListItem(admx_policy, this_policyname, this_key, ENABLED_LIST_XPATH, policy_filedata):
                    this_policy_setting = 'Enabled'
                    log.debug('{0} is enabled'.format(this_policyname))
                    if this_policynamespace not in policy_vals:
                        policy_vals[this_policynamespace] = {}
                    policy_vals[this_policynamespace][this_policyname] = this_policy_setting
            if DISABLED_LIST_XPATH(admx_policy) and this_policy_setting == 'Not Configured':
                element_only_enabled_disabled = False
                explicit_enable_disable_value_setting = True
                if _checkListItem(admx_policy, this_policyname, this_key, DISABLED_LIST_XPATH, policy_filedata):
                    this_policy_setting = 'Disabled'
                    log.debug('{0} is disabled'.format(this_policyname))
                    if this_policynamespace not in policy_vals:
                        policy_vals[this_policynamespace] = {}
                    policy_vals[this_policynamespace][this_policyname] = this_policy_setting

            if not explicit_enable_disable_value_setting and this_valuename:
                # the policy has a key/valuename but no explicit enabled/Disabled
                # Value or List
                # these seem to default to a REG_DWORD 1 = "Enabled" **del. = "Disabled"
                if _regexSearchRegPolData(re.escape(_buildKnownDataSearchString(this_key,
                                                                                this_valuename,
                                                                                'REG_DWORD',
                                                                                '1')),
                                          policy_filedata):
                    this_policy_setting = 'Enabled'
                    log.debug('{0} is enabled'.format(this_policyname))
                    if this_policynamespace not in policy_vals:
                        policy_vals[this_policynamespace] = {}
                    policy_vals[this_policynamespace][this_policyname] = this_policy_setting
                elif _regexSearchRegPolData(re.escape(_buildKnownDataSearchString(this_key,
                                                                                  this_valuename,
                                                                                  'REG_DWORD',
                                                                                  None,
                                                                                  check_deleted=True)),
                                            policy_filedata):
                    this_policy_setting = 'Disabled'
                    log.debug('{0} is disabled'.format(this_policyname))
                    if this_policynamespace not in policy_vals:
                        policy_vals[this_policynamespace] = {}
                    policy_vals[this_policynamespace][this_policyname] = this_policy_setting

            if ELEMENTS_XPATH(admx_policy):
                if element_only_enabled_disabled or this_policy_setting == 'Enabled':
                    # TODO does this need to be modified based on the 'required' attribute?
                    required_elements = {}
                    configured_elements = {}
                    policy_disabled_elements = 0
                    for elements_item in ELEMENTS_XPATH(admx_policy):
                        for child_item in elements_item.getchildren():
                            this_element_name = _getFullPolicyName(child_item,
                                                                   child_item.attrib['id'],
                                                                   return_full_policy_names,
                                                                   adml_policy_resources)
                            required_elements[this_element_name] = None
                            child_key = this_key
                            child_valuename = this_valuename
                            if 'key' in child_item.attrib:
                                child_key = child_item.attrib['key']
                            if 'valueName' in child_item.attrib:
                                child_valuename = child_item.attrib['valueName']

                            if etree.QName(child_item).localname == 'boolean':
                                # https://msdn.microsoft.com/en-us/library/dn605978(v=vs.85).aspx
                                if child_item.getchildren():
                                    if TRUE_VALUE_XPATH(child_item) and this_element_name not in configured_elements:
                                        if _checkValueItemParent(child_item,
                                                                 this_policyname,
                                                                 child_key,
                                                                 child_valuename,
                                                                 TRUE_VALUE_XPATH,
                                                                 policy_filedata):
                                            configured_elements[this_element_name] = True
                                            msg = 'element {0} is configured true'
                                            log.debug(msg.format(child_item.attrib['id']))
                                    if FALSE_VALUE_XPATH(child_item) and this_element_name not in configured_elements:
                                        if _checkValueItemParent(child_item,
                                                                 this_policyname,
                                                                 child_key,
                                                                 child_valuename,
                                                                 FALSE_VALUE_XPATH,
                                                                 policy_filedata):
                                            configured_elements[this_element_name] = False
                                            policy_disabled_elements = policy_disabled_elements + 1
                                            msg = 'element {0} is configured false'
                                            log.debug(msg.format(child_item.attrib['id']))
                                    # WARNING - no standard ADMX files use true/falseList
                                    # so this hasn't actually been tested
                                    if TRUE_LIST_XPATH(child_item) and this_element_name not in configured_elements:
                                        log.debug('checking trueList')
                                        if _checkListItem(child_item,
                                                          this_policyname,
                                                          this_key,
                                                          TRUE_LIST_XPATH,
                                                          policy_filedata):
                                            configured_elements[this_element_name] = True
                                            msg = 'element {0} is configured true'
                                            log.debug(msg.format(child_item.attrib['id']))
                                    if FALSE_LIST_XPATH(child_item) and this_element_name not in configured_elements:
                                        log.debug('checking falseList')
                                        if _checkListItem(child_item,
                                                          this_policyname,
                                                          this_key,
                                                          FALSE_LIST_XPATH,
                                                          policy_filedata):
                                            configured_elements[this_element_name] = False
                                            policy_disabled_elements = policy_disabled_elements + 1
                                            msg = 'element {0} is configured false'
                                            log.debug(msg.format(child_item.attrib['id']))
                                else:
                                    if _regexSearchRegPolData(re.escape(_processValueItem(child_item,
                                                                                          child_key,
                                                                                          child_valuename,
                                                                                          admx_policy,
                                                                                          elements_item,
                                                                                          check_deleted=True)),
                                                              policy_filedata):
                                        configured_elements[this_element_name] = False
                                        policy_disabled_elements = policy_disabled_elements + 1
                                        log.debug('element {0} is configured false'.format(child_item.attrib['id']))
                                    elif _regexSearchRegPolData(re.escape(_processValueItem(child_item,
                                                                                            child_key,
                                                                                            child_valuename,
                                                                                            admx_policy,
                                                                                            elements_item,
                                                                                            check_deleted=False)),
                                                                policy_filedata):
                                        configured_elements[this_element_name] = True
                                        log.debug('element {0} is configured true'.format(child_item.attrib['id']))
                            elif etree.QName(child_item).localname == 'decimal' \
                                    or etree.QName(child_item).localname == 'text' \
                                    or etree.QName(child_item).localname == 'longDecimal' \
                                    or etree.QName(child_item).localname == 'multiText':
                                # https://msdn.microsoft.com/en-us/library/dn605987(v=vs.85).aspx
                                if _regexSearchRegPolData(re.escape(_processValueItem(child_item,
                                                                                      child_key,
                                                                                      child_valuename,
                                                                                      admx_policy,
                                                                                      elements_item,
                                                                                      check_deleted=True)),
                                                          policy_filedata):
                                    configured_elements[this_element_name] = 'Disabled'
                                    policy_disabled_elements = policy_disabled_elements + 1
                                    log.debug('element {0} is disabled'.format(child_item.attrib['id']))
                                elif _regexSearchRegPolData(re.escape(_processValueItem(child_item,
                                                                                        child_key,
                                                                                        child_valuename,
                                                                                        admx_policy,
                                                                                        elements_item,
                                                                                        check_deleted=False)),
                                                            policy_filedata):
                                    configured_value = _getDataFromRegPolData(_processValueItem(child_item,
                                                                                                child_key,
                                                                                                child_valuename,
                                                                                                admx_policy,
                                                                                                elements_item,
                                                                                                check_deleted=False),
                                                                              policy_filedata)
                                    configured_elements[this_element_name] = configured_value
                                    log.debug('element {0} is enabled, value == {1}'.format(
                                            child_item.attrib['id'],
                                            configured_value))
                            elif etree.QName(child_item).localname == 'enum':
                                if _regexSearchRegPolData(re.escape(_processValueItem(child_item,
                                                                                      child_key,
                                                                                      child_valuename,
                                                                                      admx_policy,
                                                                                      elements_item,
                                                                                      check_deleted=True)),
                                                          policy_filedata):
                                    log.debug('enum element {0} is disabled'.format(child_item.attrib['id']))
                                    configured_elements[this_element_name] = 'Disabled'
                                    policy_disabled_elements = policy_disabled_elements + 1
                                else:
                                    for enum_item in child_item.getchildren():
                                        if _checkValueItemParent(enum_item,
                                                                 child_item.attrib['id'],
                                                                 child_key,
                                                                 child_valuename,
                                                                 VALUE_XPATH,
                                                                 policy_filedata):
                                            if VALUE_LIST_XPATH(enum_item):
                                                log.debug('enum item has a valueList')
                                                if _checkListItem(enum_item,
                                                                  this_policyname,
                                                                  child_key,
                                                                  VALUE_LIST_XPATH,
                                                                  policy_filedata):
                                                    log.debug('all valueList items exist in file')
                                                    configured_elements[this_element_name] = _getAdmlDisplayName(
                                                            adml_policy_resources,
                                                            enum_item.attrib['displayName'])
                                                    break
                                            else:
                                                configured_elements[this_element_name] = _getAdmlDisplayName(
                                                        adml_policy_resources,
                                                        enum_item.attrib['displayName'])
                                                break
                            elif etree.QName(child_item).localname == 'list':
                                return_value_name = False
                                if 'explicitValue' in child_item.attrib \
                                        and child_item.attrib['explicitValue'].lower() == 'true':
                                    log.debug('explicitValue list, we will return value names')
                                    return_value_name = True
                                if _regexSearchRegPolData(re.escape(_processValueItem(child_item,
                                                                                      child_key,
                                                                                      child_valuename,
                                                                                      admx_policy,
                                                                                      elements_item,
                                                                                      check_deleted=False)
                                                                    ) + salt.utils.to_bytes(r'(?!\*\*delvals\.)'),
                                                          policy_filedata):
                                    configured_value = _getDataFromRegPolData(_processValueItem(child_item,
                                                                                                child_key,
                                                                                                child_valuename,
                                                                                                admx_policy,
                                                                                                elements_item,
                                                                                                check_deleted=False),
                                                                              policy_filedata,
                                                                              return_value_name=return_value_name)
                                    configured_elements[this_element_name] = configured_value
                                    log.debug('element {0} is enabled values: {1}'.format(child_item.attrib['id'],
                                                                                          configured_value))
                                elif _regexSearchRegPolData(re.escape(_processValueItem(child_item,
                                                                                        child_key,
                                                                                        child_valuename,
                                                                                        admx_policy,
                                                                                        elements_item,
                                                                                        check_deleted=True)),
                                                            policy_filedata):
                                    configured_elements[this_element_name] = "Disabled"
                                    policy_disabled_elements = policy_disabled_elements + 1
                                    log.debug('element {0} is disabled'.format(child_item.attrib['id']))
                    if element_only_enabled_disabled:
                        if len(required_elements.keys()) > 0 \
                                    and len(configured_elements.keys()) == len(required_elements.keys()):
                            if policy_disabled_elements == len(required_elements.keys()):
                                log.debug('{0} is disabled by all enum elements'.format(this_policyname))
                                if this_policynamespace not in policy_vals:
                                    policy_vals[this_policynamespace] = {}
                                policy_vals[this_policynamespace][this_policyname] = 'Disabled'
                            else:
                                if this_policynamespace not in policy_vals:
                                    policy_vals[this_policynamespace] = {}
                                policy_vals[this_policynamespace][this_policyname] = configured_elements
                                log.debug('{0} is enabled by enum elements'.format(this_policyname))
                    else:
                        if this_policy_setting == 'Enabled':
                            if this_policynamespace not in policy_vals:
                                policy_vals[this_policynamespace] = {}
                            policy_vals[this_policynamespace][this_policyname] = configured_elements
            if return_full_policy_names and this_policynamespace in policy_vals and this_policyname in policy_vals[this_policynamespace]:
                if this_policynamespace not in full_names:
                    full_names[this_policynamespace] = {}
                full_names[this_policynamespace][this_policyname] = _getFullPolicyName(
                        admx_policy,
                        admx_policy.attrib['name'],
                        return_full_policy_names,
                        adml_policy_resources)
            if this_policynamespace in policy_vals and this_policyname in policy_vals[this_policynamespace]:
                if this_policynamespace not in hierarchy:
                    hierarchy[this_policynamespace] = {}
                hierarchy[this_policynamespace][this_policyname] = _build_parent_list(admx_policy,
                                                                admx_policy_definitions,
                                                                return_full_policy_names,
                                                                adml_policy_resources)
    if policy_vals and return_full_policy_names and not hierarchical_return:
        unpathed_dict = {}
        pathed_dict = {}
        for policy_namespace in list(policy_vals):
            for policy_item in list(policy_vals[policy_namespace]):
                if full_names[policy_namespace][policy_item] in policy_vals[policy_namespace]:
                    # add this item with the path'd full name
                    full_path_list = hierarchy[policy_namespace][policy_item]
                    full_path_list.reverse()
                    full_path_list.append(full_names[policy_namespace][policy_item])
                    policy_vals['\\'.join(full_path_list)] = policy_vals[policy_namespace].pop(policy_item)
                    pathed_dict[full_names[policy_namespace][policy_item]] = True
                else:
                    policy_vals[policy_namespace][full_names[policy_namespace][policy_item]] = policy_vals[policy_namespace].pop(policy_item)
                    if policy_namespace not in unpathed_dict:
                        unpathed_dict[policy_namespace] = {}
                    unpathed_dict[policy_namespace][full_names[policy_namespace][policy_item]] = policy_item
            # go back and remove any "unpathed" policies that need a full path
            for path_needed in unpathed_dict[policy_namespace]:
                # remove the item with the same full name and re-add it w/a path'd version
                full_path_list = hierarchy[policy_namespace][unpathed_dict[policy_namespace][path_needed]]
                full_path_list.reverse()
                full_path_list.append(path_needed)
                log.debug('full_path_list == {0}'.format(full_path_list))
                policy_vals['\\'.join(full_path_list)] = policy_vals[policy_namespace].pop(path_needed)
    for policy_namespace in list(policy_vals):
        if policy_vals[policy_namespace] == {}:
            policy_vals.pop(policy_namespace)
    if policy_vals and hierarchical_return:
        if hierarchy:
            for policy_namespace in hierarchy:
                for hierarchy_item in hierarchy[policy_namespace]:
                    if hierarchy_item in policy_vals[policy_namespace]:
                        tdict = {}
                        first_item = True
                        for item in hierarchy[policy_namespace][hierarchy_item]:
                            newdict = {}
                            if first_item:
                                h_policy_name = hierarchy_item
                                if return_full_policy_names:
                                    h_policy_name = full_names[policy_namespace][hierarchy_item]
                                newdict[item] = {h_policy_name: policy_vals[policy_namespace].pop(hierarchy_item)}
                                first_item = False
                            else:
                                newdict[item] = tdict
                            tdict = newdict
                        if tdict:
                            policy_vals = dictupdate.update(policy_vals, tdict)
                if policy_namespace in policy_vals and policy_vals[policy_namespace] == {}:
                    policy_vals.pop(policy_namespace)
        policy_vals = {
                        module_policy_data.admx_registry_classes[policy_class]['lgpo_section']: {
                            'Administrative Templates': policy_vals
                        }
                      }
    return policy_vals