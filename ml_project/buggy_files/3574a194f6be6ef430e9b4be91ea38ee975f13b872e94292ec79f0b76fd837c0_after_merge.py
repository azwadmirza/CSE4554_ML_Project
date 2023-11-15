def run_analysis(apk_dir, md5_hash, package):
    """Run Dynamic File Analysis"""
    analysis_result = {}
    logger.info("Dynamic File Analysis")
    capfuzz_home = os.path.join(str(Path.home()), ".capfuzz")
    web = os.path.join(capfuzz_home, 'flows', package + ".flows.txt")
    logcat = os.path.join(apk_dir, 'logcat.txt')
    xlogcat = os.path.join(apk_dir, 'x_logcat.txt')
    traffic = ''
    web_data = ''
    xlg = ''
    domains = {}
    logcat_data = []
    clipboard = []
    clip_tag = "I/CLIPDUMP-INFO-LOG"
    try:
        with io.open(web, mode='r', encoding="utf8", errors="ignore") as flip:
            web_data = flip.read()
    except:
        pass
    with io.open(logcat, mode='r', encoding="utf8", errors="ignore") as flip:
        logcat_data = flip.readlines()
        traffic = ''.join(logcat_data)
    with io.open(xlogcat, mode='r', encoding="utf8", errors="ignore") as flip:
        xlg = flip.read()
    traffic = web_data + traffic + xlg
    for log_line in logcat_data:
        if log_line.startswith(clip_tag):
            clipboard.append(log_line.replace(clip_tag, "Process ID "))
    urls = []
    # URLs My Custom regex
    url_pattern = re.compile(
        r'((?:https?://|s?ftps?://|file://|javascript:|data:|www\d{0,3}[.])[\w().=/;,#:@?&~*+!$%\'{}-]+)', re.UNICODE)
    urllist = re.findall(url_pattern, traffic.lower())
    # Domain Extraction and Malware Check
    logger.info("Performing Malware Check on extracted Domains")
    domains = malware_check(urllist)
    for url in urllist:
        if url not in urls:
            urls.append(url)

    # Email Etraction Regex
    emails = []
    regex = re.compile(r"[\w.-]+@[\w-]+\.[\w.]+")
    for email in regex.findall(traffic.lower()):
        if (email not in emails) and (not email.startswith('//')):
            if email == "yodleebanglore@gmail.com":
                pass
            else:
                emails.append(email)
    # Extract Device Data
    try:
        tar_loc = os.path.join(apk_dir, package + '.tar')
        untar_dir = os.path.join(apk_dir, 'DYNAMIC_DeviceData/')
        if not os.path.exists(untar_dir):
            os.makedirs(untar_dir)
        with tarfile.open(tar_loc) as tar:
            try:
                tar.extractall(untar_dir)
            except:
                pass
    except:
        PrintException("TAR EXTRACTION FAILED")
    # Do Static Analysis on Data from Device
    xmlfiles = ''
    sqlite_db = ''
    other_files = ''
    typ = ''
    untar_dir = os.path.join(apk_dir, 'DYNAMIC_DeviceData/')
    if not os.path.exists(untar_dir):
        os.makedirs(untar_dir)
    try:
        for dir_name, _, files in os.walk(untar_dir):
            for jfile in files:
                file_path = os.path.join(untar_dir, dir_name, jfile)
                if "+" in file_path:
                    shutil.move(file_path, file_path.replace("+", "x"))
                    file_path = file_path.replace("+", "x")
                fileparam = file_path.replace(untar_dir, '')
                if jfile == 'lib':
                    pass
                else:
                    if jfile.endswith('.xml'):
                        typ = 'xml'
                        xmlfiles += "<tr><td><a href='../View/?file=" + \
                            escape(fileparam) + "&md5=" + md5_hash + "&type=" + \
                            typ + "'>" + escape(fileparam) + "</a></td><tr>"
                    else:
                        with io.open(file_path, mode='r', encoding="utf8", errors="ignore") as flip:
                            file_cnt_sig = flip.read(6)
                        if file_cnt_sig == "SQLite":
                            typ = 'db'
                            sqlite_db += "<tr><td><a href='../View/?file=" + \
                                escape(fileparam) + "&md5=" + md5_hash + "&type=" + \
                                typ + "'>" + \
                                escape(fileparam) + "</a></td><tr>"
                        elif not jfile.endswith('.DS_Store'):
                            typ = 'others'
                            other_files += "<tr><td><a href='../View/?file=" + \
                                escape(fileparam) + "&md5=" + md5_hash + "&type=" + \
                                typ + "'>" + \
                                escape(fileparam) + "</a></td><tr>"
    except:
        PrintException("Dynamic File Analysis")
    analysis_result["urls"] = urls
    analysis_result["domains"] = domains
    analysis_result["emails"] = emails
    analysis_result["clipboard"] = clipboard
    analysis_result["web_data"] = web_data
    analysis_result["xmlfiles"] = xmlfiles
    analysis_result["sqlite_db"] = sqlite_db
    analysis_result["other_files"] = other_files
    return analysis_result