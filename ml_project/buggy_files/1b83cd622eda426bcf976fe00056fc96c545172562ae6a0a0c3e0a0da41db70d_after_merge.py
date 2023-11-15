def _writeAdminTemplateRegPolFile(admtemplate_data,
                                  admtemplate_namespace_data,
                                  admx_policy_definitions=None,
                                  adml_policy_resources=None,
                                  display_language='en-US',
                                  registry_class='Machine'):
    u'''
    helper function to prep/write adm template data to the Registry.pol file

    each file begins with REGFILE_SIGNATURE (u'\u5250\u6765') and
    REGISTRY_FILE_VERSION (u'\x01\00')

    https://msdn.microsoft.com/en-us/library/aa374407(VS.85).aspx
    [Registry Path<NULL>;Reg Value<NULL>;Reg Type<NULL>;SizeInBytes<NULL>;Data<NULL>]
    '''
    existing_data = ''
    base_policy_settings = {}
    policy_data = _policy_info()
    policySearchXpath = '//ns1:*[@id = "{0}" or @name = "{0}"]'
    try:
        if admx_policy_definitions is None or adml_policy_resources is None:
            admx_policy_definitions, adml_policy_resources = _processPolicyDefinitions(
                    display_language=display_language)
        base_policy_settings = _checkAllAdmxPolicies(registry_class,
                                                     admx_policy_definitions,
                                                     adml_policy_resources,
                                                     return_full_policy_names=False,
                                                     hierarchical_return=False,
                                                     return_not_configured=False)
        log.debug('preparing to loop through policies requested to be configured')
        for adm_namespace in admtemplate_data:
            for adm_policy in admtemplate_data[adm_namespace]:
                if str(admtemplate_data[adm_namespace][adm_policy]).lower() == 'not configured':
                    if base_policy_settings.get(adm_namespace, {}).pop(adm_policy, None) is not None:
                        log.debug('Policy "{0}" removed'.format(adm_policy))
                else:
                    log.debug('adding {0} to base_policy_settings'.format(adm_policy))
                    if adm_namespace not in base_policy_settings:
                        base_policy_settings[adm_namespace] = {}
                    base_policy_settings[adm_namespace][adm_policy] = admtemplate_data[adm_namespace][adm_policy]
        for adm_namespace in base_policy_settings:
            for admPolicy in base_policy_settings[adm_namespace]:
                log.debug('working on admPolicy {0}'.format(admPolicy))
                explicit_enable_disable_value_setting = False
                this_key = None
                this_valuename = None
                if str(base_policy_settings[adm_namespace][admPolicy]).lower() == 'disabled':
                    log.debug('time to disable {0}'.format(admPolicy))
                    this_policy = admx_policy_definitions.xpath(policySearchXpath.format(admPolicy), namespaces={'ns1': adm_namespace})
                    if this_policy:
                        this_policy = this_policy[0]
                        if 'class' in this_policy.attrib:
                            if this_policy.attrib['class'] == registry_class or this_policy.attrib['class'] == 'Both':
                                if 'key' in this_policy.attrib:
                                    this_key = this_policy.attrib['key']
                                else:
                                    msg = 'policy item {0} does not have the required "key" attribute'
                                    log.error(msg.format(this_policy.attrib))
                                    break
                                if 'valueName' in this_policy.attrib:
                                    this_valuename = this_policy.attrib['valueName']
                                if DISABLED_VALUE_XPATH(this_policy):
                                    # set the disabled value in the registry.pol file
                                    explicit_enable_disable_value_setting = True
                                    disabled_value_string = _checkValueItemParent(this_policy,
                                                                                  admPolicy,
                                                                                  this_key,
                                                                                  this_valuename,
                                                                                  DISABLED_VALUE_XPATH,
                                                                                  None,
                                                                                  check_deleted=False,
                                                                                  test_item=False)
                                    existing_data = _policyFileReplaceOrAppend(disabled_value_string,
                                                                               existing_data)
                                if DISABLED_LIST_XPATH(this_policy):
                                    explicit_enable_disable_value_setting = True
                                    disabled_list_strings = _checkListItem(this_policy,
                                                                           admPolicy,
                                                                           this_key,
                                                                           DISABLED_LIST_XPATH,
                                                                           None,
                                                                           test_items=False)
                                    log.debug('working with disabledList portion of {0}'.format(admPolicy))
                                    existing_data = _policyFileReplaceOrAppendList(disabled_list_strings,
                                                                                   existing_data)
                                if not explicit_enable_disable_value_setting and this_valuename:
                                    disabled_value_string = _buildKnownDataSearchString(this_key,
                                                                                        this_valuename,
                                                                                        'REG_DWORD',
                                                                                        None,
                                                                                        check_deleted=True)
                                    existing_data = _policyFileReplaceOrAppend(disabled_value_string,
                                                                               existing_data)
                                if ELEMENTS_XPATH(this_policy):
                                    log.debug('checking elements of {0}'.format(admPolicy))
                                    for elements_item in ELEMENTS_XPATH(this_policy):
                                        for child_item in elements_item.getchildren():
                                            child_key = this_key
                                            child_valuename = this_valuename
                                            if 'key' in child_item.attrib:
                                                child_key = child_item.attrib['key']
                                            if 'valueName' in child_item.attrib:
                                                child_valuename = child_item.attrib['valueName']
                                            if etree.QName(child_item).localname == 'boolean' \
                                                    and (TRUE_LIST_XPATH(child_item) or FALSE_LIST_XPATH(child_item)):
                                                # WARNING: no OOB adm files use true/falseList items
                                                # this has not been fully vetted
                                                temp_dict = {'trueList': TRUE_LIST_XPATH, 'falseList': FALSE_LIST_XPATH}
                                                for this_list in temp_dict:
                                                    disabled_list_strings = _checkListItem(
                                                            child_item,
                                                            admPolicy,
                                                            child_key,
                                                            temp_dict[this_list],
                                                            None,
                                                            test_items=False)
                                                    log.debug('working with {1} portion of {0}'.format(
                                                            admPolicy,
                                                            this_list))
                                                    existing_data = _policyFileReplaceOrAppendList(
                                                            disabled_list_strings,
                                                            existing_data)
                                            elif etree.QName(child_item).localname == 'boolean' \
                                                    or etree.QName(child_item).localname == 'decimal' \
                                                    or etree.QName(child_item).localname == 'text' \
                                                    or etree.QName(child_item).localname == 'longDecimal' \
                                                    or etree.QName(child_item).localname == 'multiText' \
                                                    or etree.QName(child_item).localname == 'enum':
                                                disabled_value_string = _processValueItem(child_item,
                                                                                          child_key,
                                                                                          child_valuename,
                                                                                          this_policy,
                                                                                          elements_item,
                                                                                          check_deleted=True)
                                                msg = 'I have disabled value string of {0}'
                                                log.debug(msg.format(disabled_value_string))
                                                existing_data = _policyFileReplaceOrAppend(
                                                        disabled_value_string,
                                                        existing_data)
                                            elif etree.QName(child_item).localname == 'list':
                                                disabled_value_string = _processValueItem(child_item,
                                                                                          child_key,
                                                                                          child_valuename,
                                                                                          this_policy,
                                                                                          elements_item,
                                                                                          check_deleted=True)
                                                msg = 'I have disabled value string of {0}'
                                                log.debug(msg.format(disabled_value_string))
                                                existing_data = _policyFileReplaceOrAppend(
                                                        disabled_value_string,
                                                        existing_data)
                            else:
                                msg = 'policy {0} was found but it does not appear to be valid for the class {1}'
                                log.error(msg.format(admPolicy, registry_class))
                        else:
                            msg = 'policy item {0} does not have the requried "class" attribute'
                            log.error(msg.format(this_policy.attrib))
                else:
                    log.debug('time to enable and set the policy "{0}"'.format(admPolicy))
                    this_policy = admx_policy_definitions.xpath(policySearchXpath.format(admPolicy), namespaces={'ns1': adm_namespace})
                    log.debug('found this_policy == {0}'.format(this_policy))
                    if this_policy:
                        this_policy = this_policy[0]
                        if 'class' in this_policy.attrib:
                            if this_policy.attrib['class'] == registry_class or this_policy.attrib['class'] == 'Both':
                                if 'key' in this_policy.attrib:
                                    this_key = this_policy.attrib['key']
                                else:
                                    msg = 'policy item {0} does not have the required "key" attribute'
                                    log.error(msg.format(this_policy.attrib))
                                    break
                                if 'valueName' in this_policy.attrib:
                                    this_valuename = this_policy.attrib['valueName']

                                if ENABLED_VALUE_XPATH(this_policy):
                                    explicit_enable_disable_value_setting = True
                                    enabled_value_string = _checkValueItemParent(this_policy,
                                                                                 admPolicy,
                                                                                 this_key,
                                                                                 this_valuename,
                                                                                 ENABLED_VALUE_XPATH,
                                                                                 None,
                                                                                 check_deleted=False,
                                                                                 test_item=False)
                                    existing_data = _policyFileReplaceOrAppend(
                                            enabled_value_string,
                                            existing_data)
                                if ENABLED_LIST_XPATH(this_policy):
                                    explicit_enable_disable_value_setting = True
                                    enabled_list_strings = _checkListItem(this_policy,
                                                                          admPolicy,
                                                                          this_key,
                                                                          ENABLED_LIST_XPATH,
                                                                          None,
                                                                          test_items=False)
                                    log.debug('working with enabledList portion of {0}'.format(admPolicy))
                                    existing_data = _policyFileReplaceOrAppendList(
                                            enabled_list_strings,
                                            existing_data)
                                if not explicit_enable_disable_value_setting and this_valuename:
                                    enabled_value_string = _buildKnownDataSearchString(this_key,
                                                                                       this_valuename,
                                                                                       'REG_DWORD',
                                                                                       '1',
                                                                                       check_deleted=False)
                                    existing_data = _policyFileReplaceOrAppend(
                                            enabled_value_string,
                                            existing_data)
                                if ELEMENTS_XPATH(this_policy):
                                    for elements_item in ELEMENTS_XPATH(this_policy):
                                        for child_item in elements_item.getchildren():
                                            child_key = this_key
                                            child_valuename = this_valuename
                                            if 'key' in child_item.attrib:
                                                child_key = child_item.attrib['key']
                                            if 'valueName' in child_item.attrib:
                                                child_valuename = child_item.attrib['valueName']
                                            if child_item.attrib['id'] in base_policy_settings[adm_namespace][admPolicy]:
                                                if etree.QName(child_item).localname == 'boolean' and (
                                                        TRUE_LIST_XPATH(child_item) or FALSE_LIST_XPATH(child_item)):
                                                    list_strings = []
                                                    if base_policy_settings[adm_namespace][admPolicy][child_item.attrib['id']]:
                                                        list_strings = _checkListItem(child_item,
                                                                                      admPolicy,
                                                                                      child_key,
                                                                                      TRUE_LIST_XPATH,
                                                                                      None,
                                                                                      test_items=False)
                                                        log.debug('working with trueList portion of {0}'.format(admPolicy))
                                                    else:
                                                        list_strings = _checkListItem(child_item,
                                                                                      admPolicy,
                                                                                      child_key,
                                                                                      FALSE_LIST_XPATH,
                                                                                      None,
                                                                                      test_items=False)
                                                    existing_data = _policyFileReplaceOrAppendList(
                                                            list_strings,
                                                            existing_data)
                                                elif etree.QName(child_item).localname == 'boolean' and (
                                                        TRUE_VALUE_XPATH(child_item) or FALSE_VALUE_XPATH(child_item)):
                                                    value_string = ''
                                                    if base_policy_settings[adm_namespace][admPolicy][child_item.attrib['id']]:
                                                        value_string = _checkValueItemParent(child_item,
                                                                                             admPolicy,
                                                                                             child_key,
                                                                                             child_valuename,
                                                                                             TRUE_VALUE_XPATH,
                                                                                             None,
                                                                                             check_deleted=False,
                                                                                             test_item=False)
                                                    else:
                                                        value_string = _checkValueItemParent(child_item,
                                                                                             admPolicy,
                                                                                             child_key,
                                                                                             child_valuename,
                                                                                             FALSE_VALUE_XPATH,
                                                                                             None,
                                                                                             check_deleted=False,
                                                                                             test_item=False)
                                                    existing_data = _policyFileReplaceOrAppend(
                                                            value_string,
                                                            existing_data)
                                                elif etree.QName(child_item).localname == 'boolean' \
                                                        or etree.QName(child_item).localname == 'decimal' \
                                                        or etree.QName(child_item).localname == 'text' \
                                                        or etree.QName(child_item).localname == 'longDecimal' \
                                                        or etree.QName(child_item).localname == 'multiText':
                                                    enabled_value_string = _processValueItem(
                                                            child_item,
                                                            child_key,
                                                            child_valuename,
                                                            this_policy,
                                                            elements_item,
                                                            check_deleted=False,
                                                            this_element_value=base_policy_settings[adm_namespace][admPolicy][child_item.attrib['id']])
                                                    msg = 'I have enabled value string of {0}'
                                                    log.debug(msg.format([enabled_value_string]))
                                                    existing_data = _policyFileReplaceOrAppend(
                                                            enabled_value_string,
                                                            existing_data)
                                                elif etree.QName(child_item).localname == 'enum':
                                                    for enum_item in child_item.getchildren():
                                                        if base_policy_settings[adm_namespace][admPolicy][child_item.attrib['id']] == \
                                                                _getAdmlDisplayName(adml_policy_resources,
                                                                                    enum_item.attrib['displayName']
                                                                                    ).strip():
                                                            enabled_value_string = _checkValueItemParent(
                                                                    enum_item,
                                                                    child_item.attrib['id'],
                                                                    child_key,
                                                                    child_valuename,
                                                                    VALUE_XPATH,
                                                                    None,
                                                                    check_deleted=False,
                                                                    test_item=False)
                                                            existing_data = _policyFileReplaceOrAppend(
                                                                    enabled_value_string,
                                                                    existing_data)
                                                            if VALUE_LIST_XPATH(enum_item):
                                                                enabled_list_strings = _checkListItem(enum_item,
                                                                                                      admPolicy,
                                                                                                      child_key,
                                                                                                      VALUE_LIST_XPATH,
                                                                                                      None,
                                                                                                      test_items=False)
                                                                msg = 'working with valueList portion of {0}'
                                                                log.debug(msg.format(child_item.attrib['id']))
                                                                existing_data = _policyFileReplaceOrAppendList(
                                                                        enabled_list_strings,
                                                                        existing_data)
                                                            break
                                                elif etree.QName(child_item).localname == 'list':
                                                    enabled_value_string = _processValueItem(
                                                            child_item,
                                                            child_key,
                                                            child_valuename,
                                                            this_policy,
                                                            elements_item,
                                                            check_deleted=False,
                                                            this_element_value=base_policy_settings[adm_namespace][admPolicy][child_item.attrib['id']])
                                                    msg = 'I have enabled value string of {0}'
                                                    log.debug(msg.format([enabled_value_string]))
                                                    existing_data = _policyFileReplaceOrAppend(
                                                            enabled_value_string,
                                                            existing_data,
                                                            append_only=True)
        _write_regpol_data(existing_data,
                           policy_data.admx_registry_classes[registry_class]['policy_path'],
                           policy_data.gpt_ini_path,
                           policy_data.admx_registry_classes[registry_class]['gpt_extension_location'],
                           policy_data.admx_registry_classes[registry_class]['gpt_extension_guid'])
    except Exception as e:
        log.error('Unhandled exception {0} occurred while attempting to write Adm Template Policy File'.format(e))
        return False
    return True