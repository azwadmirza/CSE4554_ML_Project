def res_analysis(app_dir):
    """Perform the elf analysis."""
    try:
        logger.info("Static Android Resource Analysis Started")
        elf_desc = {
            'html_infected':
                (
                    'Found html files infected by malware.',
                    'high',
                    'The built environment was probably infected by malware, The html file '
                    'used in this APK is infected.'
                ),
        }
        html_an_dic = {}
        for k in list(elf_desc.keys()):
            html_an_dic[k] = []
        resraw = os.path.join(app_dir, "res", "raw")
        assets = os.path.join(app_dir, "assets")
        for resdir in (resraw, assets):
            if os.path.exists(resdir) and os.path.isdir(resdir):
                for pdir, dirl, filel in os.walk(resdir):
                    for filename in filel:
                        if filename.endswith(".htm") or filename.endswith(".html"):
                            try:
                                filepath = os.path.join(pdir, filename)
                                buf = ""
                                with io.open(filepath, mode='rb') as filp:
                                    buf = filp.read()
                                if "svchost.exe" in buf:
                                    html_an_dic['html_infected'].append(
                                        filepath.replace(app_dir, ""))
                            except Exception as e:
                                pass
        res = []
        for k, filelist in list(html_an_dic.items()):
            if len(filelist):
                descs = elf_desc.get(k)
                res.append({'title': descs[0],
                            'stat': descs[1],
                            'desc': descs[2],
                            'file': " ".join(filelist),
                            })
        return res

    except:
        PrintException("[ERROR] Performing Resourse Analysis")