def report(request):
    """Dynamic Analysis Report Generation"""
    logger.info("Dynamic Analysis Report Generation")
    try:
        if request.method == 'GET':
            md5_hash = request.GET['md5']
            package = request.GET['pkg']
            if re.findall(r";|\$\(|\|\||&&", package):
                return print_n_send_error_response(request, "Possible RCE Attack")
            if re.match('^[0-9a-f]{32}$', md5_hash):
                app_dir = os.path.join(
                    settings.UPLD_DIR, md5_hash + '/')  # APP DIRECTORY
                download_dir = settings.DWD_DIR
                droidmon_api_loc = os.path.join(app_dir, 'x_logcat.txt')
                api_analysis_result = api_analysis(package, droidmon_api_loc)
                analysis_result = run_analysis(app_dir, md5_hash, package)
                download(md5_hash, download_dir, app_dir, package)
                # Only After Download Process is Done
                imgs = []
                act_imgs = []
                act = {}
                expact_imgs = []
                exp_act = {}
                if os.path.exists(os.path.join(download_dir, md5_hash + "-screenshots-apk/")):
                    try:
                        imp_path = os.path.join(
                            download_dir, md5_hash + "-screenshots-apk/")
                        for img in os.listdir(imp_path):
                            if img.endswith(".png"):
                                if img.startswith("act"):
                                    act_imgs.append(img)
                                elif img.startswith("expact"):
                                    expact_imgs.append(img)
                                else:
                                    imgs.append(img)
                        static_android_db = StaticAnalyzerAndroid.objects.filter(
                            MD5=md5_hash)
                        if static_android_db.exists():
                            logger.info(
                                "\nFetching Exported Activity & Activity List from DB")
                            exported_act = python_list(
                                static_android_db[0].EXPORTED_ACT)
                            act_desc = python_list(
                                static_android_db[0].ACTIVITIES)
                            if act_imgs:
                                if len(act_imgs) == len(act_desc):
                                    act = dict(list(zip(act_imgs, act_desc)))
                            if expact_imgs:
                                if len(expact_imgs) == len(exported_act):
                                    exp_act = dict(
                                        list(zip(expact_imgs, exported_act)))
                        else:
                            logger.warning("Entry does not exists in the DB.")
                    except:
                        PrintException("Screenshot Sorting")
                context = {'md5': md5_hash,
                           'emails': analysis_result["emails"],
                           'urls': analysis_result["urls"],
                           'domains': analysis_result["domains"],
                           'clipboard': analysis_result["clipboard"],
                           'http': analysis_result["web_data"],
                           'xml': analysis_result["xmlfiles"],
                           'sqlite': analysis_result["sqlite_db"],
                           'others': analysis_result["other_files"],
                           'imgs': imgs,
                           'acttest': act,
                           'expacttest': exp_act,
                           'net': api_analysis_result["api_net"],
                           'base64': api_analysis_result["api_base64"],
                           'crypto': api_analysis_result["api_crypto"],
                           'fileio': api_analysis_result["api_fileio"],
                           'binder': api_analysis_result["api_binder"],
                           'divinfo': api_analysis_result["api_deviceinfo"],
                           'cntval': api_analysis_result["api_cntvl"],
                           'sms': api_analysis_result["api_sms"],
                           'sysprop': api_analysis_result["api_sysprop"],
                           'dexload': api_analysis_result["api_dexloader"],
                           'reflect': api_analysis_result["api_reflect"],
                           'sysman': api_analysis_result["api_acntmnger"],
                           'process': api_analysis_result["api_cmd"],
                           'pkg': package,
                           'title': 'Dynamic Analysis'}
                template = "dynamic_analysis/dynamic_analysis.html"
                return render(request, template, context)
            else:
                return print_n_send_error_response(request, "Invalid Scan Hash")
        else:
            return print_n_send_error_response(request, "Only GET allowed")
    except:
        PrintException("Dynamic Analysis Report Generation")
        return print_n_send_error_response(request, "Error Geneating Dynamic Analysis Report")