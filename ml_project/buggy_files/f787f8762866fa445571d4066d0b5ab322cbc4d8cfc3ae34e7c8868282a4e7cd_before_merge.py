def dump_data(request):
    """Downloading Application Data from Device"""
    logger.info("Downloading Application Data from Device")
    try:
        if request.method == 'POST':
            data = {}
            package = request.POST['pkg']
            md5_hash = request.POST['md5']
            if re.match('^[0-9a-f]{32}$', md5_hash):
                if re.findall(r";|\$\(|\|\||&&", package):
                    logger.info("[ATTACK] Possible RCE")
                    return HttpResponseRedirect('/error/')
                base_dir = settings.BASE_DIR
                apk_dir = os.path.join(settings.UPLD_DIR, md5_hash + '/')
                # Let's try to close Proxy a bit early as we don't have much
                # control on the order of thread execution
                stop_capfuzz(settings.PORT)
                logger.info("Deleting Dump Status File")
                adb_command(["rm", "/sdcard/mobsec_status"], True)
                logger.info("Creating TAR of Application Files.")
                adb_command(["am", "startservice", "-a", package,
                             "opensecurity.ajin.datapusher/.GetPackageLocation"], True)
                logger.info("Waiting for TAR dump to complete...")
                if settings.ANDROID_DYNAMIC_ANALYZER == "MobSF_REAL_DEVICE":
                    timeout = settings.DEVICE_TIMEOUT
                else:
                    timeout = settings.VM_TIMEOUT
                start_time = time.time()
                while True:
                    current_time = time.time()
                    if b"MOBSEC-TAR-CREATED" in adb_command(["cat", "/sdcard/mobsec_status"], shell=True):
                        break
                    if (current_time - start_time) > timeout:
                        logger.error("TAR Generation Failed. Process timed out.")
                        break
                logger.info("Dumping Application Files from Device/VM")
                adb_command(["pull", "/data/local/" + package +
                             ".tar", apk_dir + package + ".tar"])
                if settings.ANDROID_DYNAMIC_ANALYZER == "MobSF_AVD":
                    logger.info("Removing package")
                    adb_command(["uninstall", package])
                    stop_avd()
                logger.info("Stopping ADB")
                adb_command(["kill-server"])
                data = {'dump': 'yes'}
                return HttpResponse(json.dumps(data), content_type='application/json')
            else:
                return HttpResponseRedirect('/error/')
        else:
            return HttpResponseRedirect('/error/')
    except:
        PrintException("[ERROR] Downloading Application Data from Device")
        return HttpResponseRedirect('/error/')