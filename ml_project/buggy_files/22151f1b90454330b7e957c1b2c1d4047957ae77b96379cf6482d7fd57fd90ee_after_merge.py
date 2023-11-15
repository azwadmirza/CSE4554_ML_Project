def get_env(request):
    """Get Dynamic Analysis Environment for Android"""
    logger.info("Setting up Dynamic Analysis Environment")
    try:
        if request.method == 'POST':
            data = {}
            md5_hash = request.POST['md5']
            package = request.POST['pkg']
            launcher = request.POST['lng']
            if re.findall(r";|\$\(|\|\||&&", package) or re.findall(r";|\$\(|\|\||&&", launcher):
                return print_n_send_error_response(request, "Possible RCE Attack", True)
            if re.match('^[0-9a-f]{32}$', md5_hash):
                base_dir = settings.BASE_DIR
                app_dir = os.path.join(
                    settings.UPLD_DIR, md5_hash + '/')  # APP DIRECTORY
                app_file = md5_hash + '.apk'  # NEW FILENAME
                app_path = app_dir + app_file  # APP PATH
                adb = getADB()
                if settings.ANDROID_DYNAMIC_ANALYZER == "MobSF_AVD":
                    proxy_ip = '127.0.0.1'
                else:
                    proxy_ip = settings.PROXY_IP  # Proxy IP
                start_proxy(settings.PORT, package)
                # vm needs the connect function
                try:
                    if not settings.ANDROID_DYNAMIC_ANALYZER == "MobSF_AVD":
                        connect()
                except Exception as exp:
                    data = {'ready': 'no',
                            'msg': 'Cannot Connect to the VM/Device.',
                            'error': str(exp)}
                    return HttpResponse(json.dumps(data), content_type='application/json')
                # Change True to support non-activity components
                install_and_run(app_path, package, launcher, True)
                screen_width, screen_width = get_res()
                data = {'ready': 'yes',
                        'screen_witdth': screen_width,
                        'screen_height': screen_width, }
                return HttpResponse(json.dumps(data), content_type='application/json')
            else:
                return print_n_send_error_response(request, "Invalid Scan Hash", True)
        else:
            return print_n_send_error_response(request, "Only POST allowed", True)
    except:
        PrintException("Setting up Dynamic Analysis Environment")
        return print_n_send_error_response(request, "Environment Setup Failed", True)