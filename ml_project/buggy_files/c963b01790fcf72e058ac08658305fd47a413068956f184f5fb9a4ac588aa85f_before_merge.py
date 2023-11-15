def mobsf_ca(request):
    """Install and Remove MobSF Proxy RootCA"""
    try:
        if request.method == 'POST':
            data = {}
            act = request.POST['action']
            rootca = get_ca_dir()
            adb = getADB()
            if act == "install":
                logger.info("Installing MobSF RootCA")
                adb_command(
                    ["push", rootca, "/data/local/tmp/" + settings.ROOT_CA])
                if settings.ANDROID_DYNAMIC_ANALYZER == "MobSF_AVD":
                    # For some reason, avd emulator does not have cp binary
                    adb_command(["/data/local/tmp/busybox", "cp",
                                 "/data/local/tmp/" + settings.ROOT_CA,
                                 "/system/etc/security/cacerts/" + settings.ROOT_CA], True)
                    adb_command(["chmod", "644",
                                 "/system/etc/security/cacerts/" + settings.ROOT_CA], True)
                else:
                    adb_command(["su",
                                 "-c",
                                 "cp",
                                 "/data/local/tmp/" + settings.ROOT_CA,
                                 "/system/etc/security/cacerts/" + settings.ROOT_CA], True)
                    adb_command(["su",
                                 "-c",
                                 "chmod",
                                 "644",
                                 "/system/etc/security/cacerts/" + settings.ROOT_CA], True)
                adb_command(
                    ["rm", "/data/local/tmp/" + settings.ROOT_CA], True)
                data = {'ca': 'installed'}
            elif act == "remove":
                logger.info("Removing MobSF RootCA")
                if settings.ANDROID_DYNAMIC_ANALYZER == "MobSF_AVD":
                    adb_command(
                        ["rm", "/system/etc/security/cacerts/" + settings.ROOT_CA], True)
                else:
                    adb_command(["su",
                                 "-c",
                                 "rm",
                                 "/system/etc/security/cacerts/" + settings.ROOT_CA], True)
                data = {'ca': 'removed'}
            return HttpResponse(json.dumps(data), content_type='application/json')
        else:
            return HttpResponseRedirect('/error/')
    except:
        PrintException("[ERROR] MobSF RootCA Handler")
        return HttpResponseRedirect('/error/')