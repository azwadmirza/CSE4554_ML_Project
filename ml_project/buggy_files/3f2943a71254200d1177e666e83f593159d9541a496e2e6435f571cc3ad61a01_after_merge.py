def manifest_data(mfxml):
    """Extract manifest data."""
    try:
        logger.info("Extracting Manifest Data")
        svc = []
        act = []
        brd = []
        cnp = []
        lib = []
        perm = []
        cat = []
        icons = []
        dvm_perm = {}
        package = ''
        minsdk = ''
        maxsdk = ''
        targetsdk = ''
        mainact = ''
        androidversioncode = ''
        androidversionname = ''
        applications = mfxml.getElementsByTagName("application")
        permissions = mfxml.getElementsByTagName("uses-permission")
        manifest = mfxml.getElementsByTagName("manifest")
        activities = mfxml.getElementsByTagName("activity")
        services = mfxml.getElementsByTagName("service")
        providers = mfxml.getElementsByTagName("provider")
        receivers = mfxml.getElementsByTagName("receiver")
        libs = mfxml.getElementsByTagName("uses-library")
        sdk = mfxml.getElementsByTagName("uses-sdk")
        categories = mfxml.getElementsByTagName("category")
        for node in sdk:
            minsdk = node.getAttribute("android:minSdkVersion")
            maxsdk = node.getAttribute("android:maxSdkVersion")
            # Esteve 08.08.2016 - begin - If android:targetSdkVersion is not set,
            # the default value is the one of the android:minSdkVersion
            # targetsdk=node.getAttribute("android:targetSdkVersion")
            if node.getAttribute("android:targetSdkVersion"):
                targetsdk = node.getAttribute("android:targetSdkVersion")
            else:
                targetsdk = node.getAttribute("android:minSdkVersion")
            # End
        for node in manifest:
            package = node.getAttribute("package")
            androidversioncode = node.getAttribute("android:versionCode")
            androidversionname = node.getAttribute("android:versionName")
        for activity in activities:
            act_2 = activity.getAttribute("android:name")
            act.append(act_2)
            if len(mainact) < 1:
                # ^ Fix for Shitty Manifest with more than one MAIN
                for sitem in activity.getElementsByTagName("action"):
                    val = sitem.getAttribute("android:name")
                    if val == "android.intent.action.MAIN":
                        mainact = activity.getAttribute("android:name")
                if mainact == '':
                    for sitem in activity.getElementsByTagName("category"):
                        val = sitem.getAttribute("android:name")
                        if val == "android.intent.category.LAUNCHER":
                            mainact = activity.getAttribute("android:name")

        for service in services:
            service_name = service.getAttribute("android:name")
            svc.append(service_name)

        for provider in providers:
            provider_name = provider.getAttribute("android:name")
            cnp.append(provider_name)

        for receiver in receivers:
            rec = receiver.getAttribute("android:name")
            brd.append(rec)

        for _lib in libs:
            libary = _lib.getAttribute("android:name")
            lib.append(libary)

        for category in categories:
            cat.append(category.getAttribute("android:name"))

        for application in applications:
            try:
                icon_path = application.getAttribute("android:icon")
                icons.append(icon_path)
            except:
                continue  # No icon attribute?

        for permission in permissions:
            perm.append(permission.getAttribute("android:name"))

        for i in perm:
            prm = i
            pos = i.rfind(".")
            if pos != -1:
                prm = i[pos + 1:]
            try:
                dvm_perm[i] = DVM_PERMISSIONS["MANIFEST_PERMISSION"][prm]
            except KeyError:
                dvm_perm[i] = [
                    "dangerous",
                    "Unknown permission from android reference",
                    "Unknown permission from android reference"
                ]

        man_data_dic = {
            'services': svc,
            'activities': act,
            'receivers': brd,
            'providers': cnp,
            'libraries': lib,
            'categories': cat,
            'perm': dvm_perm,
            'packagename': package,
            'mainactivity': mainact,
            'min_sdk': minsdk,
            'max_sdk': maxsdk,
            'target_sdk': targetsdk,
            'androver': androidversioncode,
            'androvername': androidversionname,
            'icons': icons
        }

        return man_data_dic
    except:
        PrintException("Extracting Manifest Data")