def take_screenshot(request):
    """Take Screenshot"""
    logger.info("Taking Screenshot")
    try:
        if request.method == 'POST':
            md5_hash = request.POST['md5']
            if re.match('^[0-9a-f]{32}$', md5_hash):
                data = {}
                rand_int = random.randint(1, 1000000)
                base_dir = settings.BASE_DIR
                # make sure that list only png from this directory
                screen_dir = os.path.join(
                    settings.UPLD_DIR, md5_hash + '/screenshots-apk/')
                if not os.path.exists(screen_dir):
                    os.makedirs(screen_dir)
                adb_command(
                    ["screencap", "-p", "/data/local/screen.png"], True)
                adb_command(["pull", "/data/local/screen.png",
                             screen_dir + "screenshot-" + str(rand_int) + ".png"])
                logger.info("Screenshot Taken")
                data = {'screenshot': 'yes'}
                return HttpResponse(json.dumps(data), content_type='application/json')
            else:
                return HttpResponseRedirect('/error/')
        else:
            return HttpResponseRedirect('/error/')
    except:
        PrintException("[ERROR] Taking Screenshot")
        return HttpResponseRedirect('/error/')