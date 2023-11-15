def manifest_analysis(mfxml, man_data_dic):
    """Analyse manifest file."""
    # pylint: disable=C0301
    try:
        logger.info("Manifest Analysis Started")
        exp_count = dict.fromkeys(["act", "ser", "bro", "cnt"], 0)
        applications = mfxml.getElementsByTagName("application")
        datas = mfxml.getElementsByTagName("data")
        intents = mfxml.getElementsByTagName("intent-filter")
        actions = mfxml.getElementsByTagName("action")
        granturipermissions = mfxml.getElementsByTagName(
            "grant-uri-permission")
        permissions = mfxml.getElementsByTagName("permission")
        ret_value = []
        ret_list = []
        exported = []
        browsable_activities = {}
        permission_dict = {}
        icon_hidden = True
        # PERMISSION
        for permission in permissions:
            if permission.getAttribute("android:protectionLevel"):
                protectionlevel = permission.getAttribute(
                    "android:protectionLevel")
                if protectionlevel == "0x00000000":
                    protectionlevel = "normal"
                elif protectionlevel == "0x00000001":
                    protectionlevel = "dangerous"
                elif protectionlevel == "0x00000002":
                    protectionlevel = "signature"
                elif protectionlevel == "0x00000003":
                    protectionlevel = "signatureOrSystem"

                permission_dict[permission.getAttribute(
                    "android:name")] = protectionlevel
            elif permission.getAttribute("android:name"):
                permission_dict[permission.getAttribute(
                    "android:name")] = "normal"

        # APPLICATIONS
        for application in applications:
            # Esteve 23.07.2016 - begin - identify permission at the
            # application level
            if application.getAttribute("android:permission"):
                perm_appl_level_exists = True
                perm_appl_level = application.getAttribute(
                    "android:permission")
            else:
                perm_appl_level_exists = False
            # End
            if application.getAttribute("android:debuggable") == "true":
                ret_list.append(("a_debuggable", tuple(), tuple(),))
            if application.getAttribute("android:allowBackup") == "true":
                ret_list.append(("a_allowbackup", tuple(), tuple(),))
            elif application.getAttribute("android:allowBackup") == "false":
                pass
            else:
                ret_list.append(("a_allowbackup_miss", tuple(), tuple(),))
            if application.getAttribute("android:testOnly") == "true":
                ret_list.append(("a_testonly", tuple(), tuple(),))
            for node in application.childNodes:
                an_or_a = ''
                if node.nodeName == 'activity':
                    itemname = 'Activity'
                    cnt_id = "act"
                    an_or_a = 'n'
                    browse_dic = get_browsable_activities(node)
                    if browse_dic["browsable"]:
                        browsable_activities[node.getAttribute(
                            "android:name")] = browse_dic
                elif node.nodeName == 'activity-alias':
                    itemname = 'Activity-Alias'
                    cnt_id = "act"
                    an_or_a = 'n'
                    browse_dic = get_browsable_activities(node)
                    if browse_dic["browsable"]:
                        browsable_activities[node.getAttribute(
                            "android:name")] = browse_dic
                elif node.nodeName == 'provider':
                    itemname = 'Content Provider'
                    cnt_id = "cnt"
                elif node.nodeName == 'receiver':
                    itemname = 'Broadcast Receiver'
                    cnt_id = "bro"
                elif node.nodeName == 'service':
                    itemname = 'Service'
                    cnt_id = "ser"
                else:
                    itemname = 'NIL'
                item = ''

                # Task Affinity
                if (
                        itemname in ['Activity', 'Activity-Alias'] and
                        node.getAttribute("android:taskAffinity")
                ):
                    item = node.getAttribute("android:name")
                    ret_list.append(("a_taskaffinity", (item,), tuple(),))

                # LaunchMode
                try:
                    affected_sdk = int(man_data_dic['min_sdk']) < ANDROID_5_0_LEVEL
                except:
                    # in case min_sdk is not defined we assume vulnerability
                    affected_sdk = True

                if (
                        affected_sdk and
                        itemname in ['Activity', 'Activity-Alias'] and
                        (
                            node.getAttribute("android:launchMode") == 'singleInstance' or
                            node.getAttribute(
                                "android:launchMode") == 'singleTask'
                        )
                ):
                    item = node.getAttribute("android:name")
                    ret_list.append(("a_launchmode", (item,), tuple(),))
                # Exported Check
                item = ''
                is_inf = False
                is_perm_exist = False
                # Esteve 23.07.2016 - begin - initialise variables to identify
                # the existence of a permission at the component level that
                # matches a permission at the manifest level
                prot_level_exist = False
                protlevel = ''
                # End
                if itemname != 'NIL':
                    if node.getAttribute("android:exported") == 'true':
                        perm = ''
                        item = node.getAttribute("android:name")
                        if node.getAttribute("android:permission"):
                            # permission exists
                            perm = (
                                '<strong>Permission: </strong>' +
                                node.getAttribute("android:permission")
                            )
                            is_perm_exist = True
                        if item != man_data_dic['mainactivity']:
                            if is_perm_exist:
                                prot = ""
                                if node.getAttribute("android:permission") in permission_dict:
                                    prot = (
                                        "</br><strong>protectionLevel: </strong>" +
                                        permission_dict[
                                            node.getAttribute("android:permission")]
                                    )
                                    # Esteve 23.07.2016 - begin - take into account protection level of the permission when claiming that a component is protected by it;
                                    # - the permission might not be defined in the application being analysed, if so, the protection level is not known;
                                    # - activities (or activity-alias) that are exported and have an unknown or normal or dangerous protection level are
                                    # included in the EXPORTED data structure for further treatment; components in this situation are also
                                    # counted as exported.
                                    prot_level_exist = True
                                    protlevel = permission_dict[
                                        node.getAttribute("android:permission")]
                                if prot_level_exist:
                                    if protlevel == 'normal':
                                        ret_list.append(
                                            ("a_prot_normal", (itemname, item, perm + prot,), (an_or_a, itemname,),))
                                        if itemname in ['Activity', 'Activity-Alias']:
                                            exported.append(item)
                                        exp_count[cnt_id] = exp_count[
                                            cnt_id] + 1
                                    elif protlevel == 'dangerous':
                                        ret_list.append(
                                            ("a_prot_danger", (itemname, item, perm + prot,), (an_or_a, itemname,),))
                                        if itemname in ['Activity', 'Activity-Alias']:
                                            exported.append(item)
                                        exp_count[cnt_id] = exp_count[
                                            cnt_id] + 1
                                    elif protlevel == 'signature':
                                        ret_list.append(
                                            ("a_prot_sign", (itemname, item, perm + prot,), (an_or_a, itemname,),))
                                    elif protlevel == 'signatureOrSystem':
                                        ret_list.append(
                                            ("a_prot_sign_sys", (itemname, item, perm + prot,), (an_or_a, itemname,),))
                                else:
                                    ret_list.append(
                                        ("a_prot_unknown", (itemname, item, perm), (an_or_a, itemname,),))
                                    if itemname in ['Activity', 'Activity-Alias']:
                                        exported.append(item)
                                    exp_count[cnt_id] = exp_count[cnt_id] + 1
                                # Esteve 23.07.2016 - end
                            else:
                                # Esteve 24.07.2016 - begin - At this point, we are dealing with components that do not have a permission neither at the component level nor at the
                                # application level. As they are exported, they
                                # are not protected.
                                if perm_appl_level_exists is False:
                                    ret_list.append(
                                        ("a_not_protected", (itemname, item), (an_or_a, itemname,),))
                                    if itemname in ['Activity', 'Activity-Alias']:
                                        exported.append(item)
                                    exp_count[cnt_id] = exp_count[cnt_id] + 1
                                # Esteve 24.07.2016 - end
                                # Esteve 24.07.2016 - begin - At this point, we are dealing with components that have a permission at the application level, but not at the component
                                #  level. Two options are possible:
                                #        1) The permission is defined at the manifest level, which allows us to differentiate the level of protection as
                                #           we did just above for permissions specified at the component level.
                                #        2) The permission is not defined at the manifest level, which means the protection level is unknown, as it is not
                                # defined in the analysed application.
                                else:
                                    perm = '<strong>Permission: </strong>' + perm_appl_level
                                    prot = ""
                                    if perm_appl_level in permission_dict:
                                        prot = "</br><strong>protectionLevel: </strong>" + \
                                            permission_dict[perm_appl_level]
                                        prot_level_exist = True
                                        protlevel = permission_dict[
                                            perm_appl_level]
                                    if prot_level_exist:
                                        if protlevel == 'normal':
                                            ret_list.append(
                                                ("a_prot_normal_appl", (itemname, item, perm + prot,), (an_or_a, itemname,),))
                                            if itemname in ['Activity', 'Activity-Alias']:
                                                exported.append(item)
                                            exp_count[cnt_id] = exp_count[
                                                cnt_id] + 1
                                        elif protlevel == 'dangerous':
                                            ret_list.append(
                                                ("a_prot_danger_appl", (itemname, item, perm + prot,), (an_or_a, itemname,),))
                                            if itemname in ['Activity', 'Activity-Alias']:
                                                exported.append(item)
                                            exp_count[cnt_id] = exp_count[
                                                cnt_id] + 1
                                        elif protlevel == 'signature':
                                            ret_list.append(
                                                ("a_prot_sign_appl", (itemname, item, perm + prot,), (an_or_a, itemname,),))
                                        elif protlevel == 'signatureOrSystem':
                                            ret_list.append(
                                                ("a_prot_sign_sys_appl", (itemname, item, perm + prot,), (an_or_a, itemname,),))
                                    else:
                                        ret_list.append(
                                            ("a_prot_unknown_appl", (itemname, item, perm), (an_or_a, itemname,),))
                                        if itemname in ['Activity', 'Activity-Alias']:
                                            exported.append(item)
                                        exp_count[cnt_id] = exp_count[
                                            cnt_id] + 1
                                # Esteve 24.07.2016 - end

                    elif node.getAttribute("android:exported") != 'false':
                        # Check for Implicitly Exported
                        # Logic to support intent-filter
                        intentfilters = node.childNodes
                        for i in intentfilters:
                            inf = i.nodeName
                            if inf == "intent-filter":
                                is_inf = True
                        if is_inf:
                            item = node.getAttribute("android:name")
                            if node.getAttribute("android:permission"):
                                # permission exists
                                perm = (
                                    '<strong>Permission: </strong>' +
                                    node.getAttribute("android:permission")
                                )
                                is_perm_exist = True
                            if item != man_data_dic['mainactivity']:
                                if is_perm_exist:
                                    prot = ""
                                    if node.getAttribute("android:permission") in permission_dict:
                                        prot = (
                                            "</br><strong>protectionLevel: </strong>" +
                                            permission_dict[
                                                node.getAttribute("android:permission")]
                                        )
                                        # Esteve 24.07.2016 - begin - take into account protection level of the permission when claiming that a component is protected by it;
                                        # - the permission might not be defined in the application being analysed, if so, the protection level is not known;
                                        # - activities (or activity-alias) that are exported and have an unknown or normal or dangerous protection level are
                                        #  included in the EXPORTED data structure for further treatment; components in this situation are also
                                        #  counted as exported.
                                        prot_level_exist = True
                                        protlevel = permission_dict[
                                            node.getAttribute("android:permission")]
                                        if prot_level_exist:
                                            if protlevel == 'normal':
                                                ret_list.append(
                                                    ("a_prot_normal", (itemname, item, perm + prot,), (an_or_a, itemname,),))
                                                if itemname in ['Activity', 'Activity-Alias']:
                                                    exported.append(item)
                                                exp_count[cnt_id] = exp_count[
                                                    cnt_id] + 1
                                            elif protlevel == 'dangerous':
                                                ret_list.append(
                                                    ("a_prot_danger", (itemname, item, perm + prot,), (an_or_a, itemname,),))
                                                if itemname in ['Activity', 'Activity-Alias']:
                                                    exported.append(item)
                                                exp_count[cnt_id] = exp_count[
                                                    cnt_id] + 1
                                            elif protlevel == 'signature':
                                                ret_list.append(
                                                    ("a_prot_sign", (itemname, item, perm + prot,), (an_or_a, itemname,),))
                                            elif protlevel == 'signatureOrSystem':
                                                ret_list.append(
                                                    ("a_prot_sign_sys", (itemname, item, perm + prot,), (an_or_a, itemname,),))
                                        else:
                                            ret_list.append(
                                                ("a_prot_unknown", (itemname, item, perm), (an_or_a, itemname,),))
                                            if itemname in ['Activity', 'Activity-Alias']:
                                                exported.append(item)
                                            exp_count[cnt_id] = exp_count[
                                                cnt_id] + 1
                                        # Esteve 24.07.2016 - end
                                else:
                                    # Esteve 24.07.2016 - begin - At this point, we are dealing with components that do not have a permission neither at the component level nor at the
                                    # application level. As they are exported,
                                    # they are not protected.
                                    if perm_appl_level_exists is False:
                                        ret_list.append(
                                            ("a_not_protected_filter", (itemname, item,), (an_or_a, itemname, itemname,),))
                                        if itemname in ['Activity', 'Activity-Alias']:
                                            exported.append(item)
                                        exp_count[cnt_id] = exp_count[
                                            cnt_id] + 1
                                    # Esteve 24.07.2016 - end
                                    # Esteve 24.07.2016 - begin - At this point, we are dealing with components that have a permission at the application level, but not at the component
                                    # level. Two options are possible:
                                    # 1) The permission is defined at the manifest level, which allows us to differentiate the level of protection as
                                    #  we did just above for permissions specified at the component level.
                                    # 2) The permission is not defined at the manifest level, which means the protection level is unknown, as it is not
                                    #  defined in the analysed application.
                                    else:
                                        perm = '<strong>Permission: </strong>' + perm_appl_level
                                        prot = ""
                                        if perm_appl_level in permission_dict:
                                            prot = "</br><strong>protectionLevel: </strong>" + \
                                                permission_dict[
                                                    perm_appl_level]
                                            prot_level_exist = True
                                            protlevel = permission_dict[
                                                perm_appl_level]
                                        if prot_level_exist:
                                            if protlevel == 'normal':
                                                ret_list.append(
                                                    ("a_prot_normal_appl", (itemname, item, perm + prot,), (an_or_a, itemname,),))
                                                if itemname in ['Activity', 'Activity-Alias']:
                                                    exported.append(item)
                                                exp_count[cnt_id] = exp_count[
                                                    cnt_id] + 1
                                            elif protlevel == 'dangerous':
                                                ret_list.append(
                                                    ("a_prot_danger_appl", (itemname, item, perm + prot,), (an_or_a, itemname,),))
                                                if itemname in ['Activity', 'Activity-Alias']:
                                                    exported.append(item)
                                                exp_count[cnt_id] = exp_count[
                                                    cnt_id] + 1
                                            elif protlevel == 'signature':
                                                ret_list.append(
                                                    ("a_prot_sign_appl", (itemname, item, perm + prot,), (an_or_a, itemname,),))
                                            elif protlevel == 'signatureOrSystem':
                                                ret_list.append(
                                                    ("a_prot_sign_sys_appl", (itemname, item, perm + prot,), (an_or_a, itemname,),))
                                        else:
                                            ret_list.append(
                                                ("a_prot_unknown_appl", (itemname, item, perm), (an_or_a, itemname,),))
                                            if itemname in ['Activity', 'Activity-Alias']:
                                                exported.append(item)
                                            exp_count[cnt_id] = exp_count[
                                                cnt_id] + 1
                                    # Esteve 24.07.2016 - end
                                    # Esteve 29.07.2016 - begin The component is not explicitly exported (android:exported is not "true"). It is not implicitly exported either (it does not
                                    # make use of an intent filter). Despite that, it could still be exported by default, if it is a content provider and the android:targetSdkVersion
                                    # is older than 17 (Jelly Bean, Android versionn 4.2). This is true regardless of the system's API level.
                                    # Finally, it must also be taken into account that, if the minSdkVersion is greater or equal than 17, this check is unnecessary, because the
                                    # app will not be run on a system where the
                                    # system's API level is below 17.
                        else:
                            if man_data_dic['min_sdk'] and man_data_dic['target_sdk'] and int(man_data_dic['min_sdk']) < ANDROID_4_2_LEVEL:
                                if itemname == 'Content Provider' and int(man_data_dic['target_sdk']) < ANDROID_4_2_LEVEL:
                                    perm = ''
                                    item = node.getAttribute("android:name")
                                    if node.getAttribute("android:permission"):
                                        # permission exists
                                        perm = '<strong>Permission: </strong>' + \
                                            node.getAttribute(
                                                "android:permission")
                                        is_perm_exist = True
                                    if is_perm_exist:
                                        prot = ""
                                        if node.getAttribute("android:permission") in permission_dict:
                                            prot = "</br><strong>protectionLevel: </strong>" + \
                                                permission_dict[
                                                    node.getAttribute("android:permission")]
                                            prot_level_exist = True
                                            protlevel = permission_dict[
                                                node.getAttribute("android:permission")]
                                        if prot_level_exist:
                                            if protlevel == 'normal':
                                                ret_list.append(
                                                    ("c_prot_normal", (itemname, item, perm + prot,), (an_or_a, itemname,),))
                                                exp_count[cnt_id] = exp_count[
                                                    cnt_id] + 1
                                            elif protlevel == 'dangerous':
                                                ret_list.append(
                                                    ("c_prot_danger", (itemname, item, perm + prot,), (an_or_a, itemname,),))
                                                exp_count[cnt_id] = exp_count[
                                                    cnt_id] + 1
                                            elif protlevel == 'signature':
                                                ret_list.append(
                                                    ("c_prot_sign", (itemname, item, perm + prot,), (an_or_a, itemname,),))
                                            elif protlevel == 'signatureOrSystem':
                                                ret_list.append(
                                                    ("c_prot_sign_sys", (itemname, item, perm + prot,), (an_or_a, itemname,),))
                                        else:
                                            ret_list.append(
                                                ("c_prot_unknown", (itemname, item, perm), (an_or_a, itemname,),))
                                            exp_count[cnt_id] = exp_count[
                                                cnt_id] + 1
                                    else:
                                        if perm_appl_level_exists is False:
                                            ret_list.append(
                                                ("c_not_protected", (itemname, item), (an_or_a, itemname,),))
                                            exp_count[cnt_id] = exp_count[
                                                cnt_id] + 1
                                        else:
                                            perm = '<strong>Permission: </strong>' + perm_appl_level
                                            prot = ""
                                            if perm_appl_level in permission_dict:
                                                prot = "</br><strong>protectionLevel: </strong>" + \
                                                    permission_dict[
                                                        perm_appl_level]
                                                prot_level_exist = True
                                                protlevel = permission_dict[
                                                    perm_appl_level]
                                            if prot_level_exist:
                                                if protlevel == 'normal':
                                                    ret_list.append(
                                                        ("c_prot_normal_appl", (itemname, item, perm + prot,), (an_or_a, itemname,),))
                                                    exp_count[cnt_id] = exp_count[
                                                        cnt_id] + 1
                                                elif protlevel == 'dangerous':
                                                    ret_list.append(
                                                        ("c_prot_danger_appl", (itemname, item, perm + prot,), (an_or_a, itemname,),))
                                                    exp_count[cnt_id] = exp_count[
                                                        cnt_id] + 1
                                                elif protlevel == 'signature':
                                                    ret_list.append(
                                                        ("c_prot_sign_appl", (itemname, item, perm + prot,), (an_or_a, itemname,),))
                                                elif protlevel == 'signatureOrSystem':
                                                    ret_list.append(
                                                        ("c_prot_sign_sys_appl", (itemname, item, perm + prot,), (an_or_a, itemname,),))
                                            else:
                                                ret_list.append(
                                                    ("c_prot_unknown_appl", (itemname, item, perm), (an_or_a, itemname,),))
                                                exp_count[cnt_id] = exp_count[
                                                    cnt_id] + 1
                                    # Esteve 29.07.2016 - end
                                    # Esteve 08.08.2016 - begin - If the content provider does not target an API version lower than 17, it could still be exported by default, depending
                                    # on the API version of the platform. If it was below 17, the content
                                    # provider would be exported by default.
                                else:
                                    if itemname == 'Content Provider' and int(man_data_dic['target_sdk']) >= 17:
                                        perm = ''
                                        item = node.getAttribute(
                                            "android:name")
                                        if node.getAttribute("android:permission"):
                                            # permission exists
                                            perm = '<strong>Permission: </strong>' + \
                                                node.getAttribute(
                                                    "android:permission")
                                            is_perm_exist = True
                                        if is_perm_exist:
                                            prot = ""
                                            if node.getAttribute("android:permission") in permission_dict:
                                                prot = "</br><strong>protectionLevel: </strong>" + \
                                                    permission_dict[
                                                        node.getAttribute("android:permission")]
                                                prot_level_exist = True
                                                protlevel = permission_dict[
                                                    node.getAttribute("android:permission")]
                                            if prot_level_exist:
                                                if protlevel == 'normal':
                                                    ret_list.append(
                                                        ("c_prot_normal_new", (itemname, item, perm + prot,), (itemname,),))
                                                    exp_count[cnt_id] = exp_count[
                                                        cnt_id] + 1
                                                if protlevel == 'dangerous':
                                                    ret_list.append(
                                                        ("c_prot_danger_new", (itemname, item, perm + prot,), (itemname,),))
                                                    exp_count[cnt_id] = exp_count[
                                                        cnt_id] + 1
                                                if protlevel == 'signature':
                                                    ret_list.append(
                                                        ("c_prot_sign_new", (itemname, item, perm + prot,), (itemname,),))
                                                if protlevel == 'signatureOrSystem':
                                                    ret_list.append(
                                                        ("c_prot_sign_sys_new", (itemname, item, perm + prot,), (an_or_a, itemname,),))
                                            else:
                                                ret_list.append(
                                                    ("c_prot_unknown_new", (itemname, item, perm), (itemname,),))
                                                exp_count[cnt_id] = exp_count[
                                                    cnt_id] + 1
                                        else:
                                            if perm_appl_level_exists is False:
                                                ret_list.append(
                                                    ("c_not_protected2", (itemname, item), (an_or_a, itemname,),))
                                                exp_count[cnt_id] = exp_count[
                                                    cnt_id] + 1
                                            else:
                                                perm = '<strong>Permission: </strong>' + perm_appl_level
                                                prot = ""
                                                if perm_appl_level in permission_dict:
                                                    prot = "</br><strong>protectionLevel: </strong>" + \
                                                        permission_dict[
                                                            perm_appl_level]
                                                    prot_level_exist = True
                                                    protlevel = permission_dict[
                                                        perm_appl_level]
                                                if prot_level_exist:
                                                    if protlevel == 'normal':
                                                        ret_list.append(
                                                            ("c_prot_normal_new_appl", (itemname, item, perm + prot,), (an_or_a, itemname,),))
                                                        exp_count[cnt_id] = exp_count[
                                                            cnt_id] + 1
                                                    elif protlevel == 'dangerous':
                                                        ret_list.append(
                                                            ("c_prot_danger_new_appl", (itemname, item, perm + prot,), (an_or_a, itemname,),))
                                                        exp_count[cnt_id] = exp_count[
                                                            cnt_id] + 1
                                                    elif protlevel == 'signature':
                                                        ret_list.append(
                                                            ("c_prot_sign_new_appl", (itemname, item, perm + prot,), (an_or_a, itemname,),))
                                                    elif protlevel == 'signatureOrSystem':
                                                        ret_list.append(
                                                            ("c_prot_sign_sys_new_appl", (itemname, item, perm + prot,), (an_or_a, itemname,),))
                                                else:
                                                    ret_list.append(
                                                        ("c_prot_unknown_new_appl", (itemname, item, perm), (an_or_a, itemname,),))
                                                    exp_count[cnt_id] = exp_count[
                                                        cnt_id] + 1
                                    # Esteve 08.08.2016 - end

        # GRANT-URI-PERMISSIONS
        for granturi in granturipermissions:
            if granturi.getAttribute("android:pathPrefix") == '/':
                ret_list.append(
                    ("a_improper_provider", ('pathPrefix=/',), tuple(),))
            elif granturi.getAttribute("android:path") == '/':
                ret_list.append(("a_improper_provider", ('path=/',), tuple(),))
            elif granturi.getAttribute("android:pathPattern") == '*':
                ret_list.append(("a_improper_provider", ('path=*',), tuple(),))
        # DATA
        for data in datas:
            if data.getAttribute("android:scheme") == "android_secret_code":
                xmlhost = data.getAttribute("android:host")
                ret_list.append(("a_dailer_code", (xmlhost,), tuple(),))

            elif data.getAttribute("android:port"):
                dataport = data.getAttribute("android:port")
                ret_list.append(("a_sms_receiver_port", (dataport,), tuple(),))
        # INTENTS
        for intent in intents:
            if intent.getAttribute("android:priority").isdigit():
                value = intent.getAttribute("android:priority")
                if int(value) > 100:
                    ret_list.append(
                        ("a_high_intent_priority", (value,), tuple(),))
        # ACTIONS
        for action in actions:
            if action.getAttribute("android:priority").isdigit():
                value = action.getAttribute("android:priority")
                if int(value) > 100:
                    ret_list.append(
                        ("a_high_action_priority", (value,), tuple(),))
        for a_key, t_name, t_desc in ret_list:
            a_template = android_manifest_desc.MANIFEST_DESC.get(a_key)
            if a_template:
                ret_value.append(
                    {"title": a_template['title'] % t_name,
                    "stat": a_template['level'],
                    "desc": a_template['description'] % t_desc,
                    "name": a_template['name'],
                    "component": t_name
                    }
                )

        for category in man_data_dic['categories']:
            if category == "android.intent.category.LAUNCHER":
                icon_hidden = False
                break

        permissons = {}
        for k, permisson in man_data_dic['perm'].items():
            permissons[k] = (
                {
                    'status': permisson[0],
                    'info': permisson[1],
                    'description': permisson[2]
                })
        # Prepare return dict
        man_an_dic = {
            'manifest_anal': ret_value,
            'exported_act': exported,
            'exported_cnt': exp_count,
            'browsable_activities': browsable_activities,
            'permissons': permissons,
            'cnt_act': len(man_data_dic['activities']),
            'cnt_pro': len(man_data_dic['providers']),
            'cnt_ser': len(man_data_dic['services']),
            'cnt_bro': len(man_data_dic['receivers']),
            'icon_hidden': icon_hidden
        }
        return man_an_dic
    except:
        PrintException("[ERROR] Performing Manifest Analysis")