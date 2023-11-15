def android_dynamic_analyzer(request):
    """Android Dynamic Analyzer View"""
    logger.info("Dynamic Analysis Started")
    try:
        if request.method == 'POST':
            md5_hash = request.POST['md5']
            package = request.POST['pkg']
            launcher = request.POST['lng']
            if re.findall(r';|\$\(|\|\||&&', package) or re.findall(r';|\$\(|\|\||&&', launcher):
                logger.info("[ATTACK] Possible RCE")
                return HttpResponseRedirect('/error/')
            if re.match('^[0-9a-f]{32}$', md5_hash):
                # Delete ScreenCast Cache
                screen_file = os.path.join(settings.SCREEN_DIR, 'screen.png')
                if os.path.exists(screen_file):
                    os.remove(screen_file)
                # Delete Contents of Screenshot Dir
                screen_dir = os.path.join(
                    settings.UPLD_DIR, md5_hash + '/screenshots-apk/')
                if os.path.isdir(screen_dir):
                    shutil.rmtree(screen_dir)
                else:
                    os.makedirs(screen_dir)
                # Start DM
                stop_capfuzz(settings.PORT)
                adb = getADB()
                is_avd = False
                if settings.ANDROID_DYNAMIC_ANALYZER == "MobSF_REAL_DEVICE":
                    logger.info("MobSF will perform Dynamic Analysis on real Android Device")
                elif settings.ANDROID_DYNAMIC_ANALYZER == "MobSF_AVD":
                    # adb, avd_path, reference_name, dup_name, emulator
                    is_avd = True
                    if not os.path.exists(settings.AVD_EMULATOR):
                        return HttpResponseRedirect('/error/')
                    if not refresh_avd():
                        return HttpResponseRedirect('/error/')
                else:
                    # Refersh VM
                    refresh_vm(settings.UUID, settings.SUUID, settings.VBOX)
                context = {'md5': md5_hash,
                           'pkg': package,
                           'lng': launcher,
                           'title': 'Start Testing',
                           'AVD': is_avd, }
                template = "dynamic_analysis/start_test.html"
                return render(request, template, context)
            else:
                return HttpResponseRedirect('/error/')
        else:
            return HttpResponseRedirect('/error/')
    except:
        PrintException("[ERROR] DynamicAnalyzer")
        return HttpResponseRedirect('/error/')