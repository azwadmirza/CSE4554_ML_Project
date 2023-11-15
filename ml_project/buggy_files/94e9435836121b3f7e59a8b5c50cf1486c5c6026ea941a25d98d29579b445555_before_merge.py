def screen_cast(request):
    """Start or Stop ScreenCast Feature"""
    logger.info("Invoking ScreenCast Service in VM/Device")
    try:
        global TCP_SERVER_MODE
        data = {}
        if request.method == 'POST':
            mode = request.POST['mode']
            if settings.ANDROID_DYNAMIC_ANALYZER == "MobSF_AVD":
                ip_address = '10.0.2.2'
            else:
                ip_address = settings.SCREEN_IP
            port = str(settings.SCREEN_PORT)
            if mode == "on":
                args = ["am",
                        "startservice",
                        "-a",
                        ip_address + ":" + port,
                        "opensecurity.screencast/.StartScreenCast"]
                data = {'status': 'on'}
                TCP_SERVER_MODE = "on"
            elif mode == "off":
                args = ["am",
                        "force-stop",
                        "opensecurity.screencast"]
                data = {'status': 'off'}
                TCP_SERVER_MODE = "off"
            if (mode in ["on", "off"]):
                try:
                    adb_command(args, True)
                    screen_trd = threading.Thread(target=screencast_service)
                    screen_trd.setDaemon(True)
                    screen_trd.start()
                except:
                    PrintException("[ERROR] Casting Screen")
                    data = {'status': 'error'}
                    return HttpResponse(json.dumps(data), content_type='application/json')
            else:
                data = {'status': 'failed'}
        else:
            data = {'status': 'failed'}
        return HttpResponse(json.dumps(data), content_type='application/json')
    except:
        PrintException("[ERROR] Casting Screen")
        return HttpResponseRedirect('/error/')