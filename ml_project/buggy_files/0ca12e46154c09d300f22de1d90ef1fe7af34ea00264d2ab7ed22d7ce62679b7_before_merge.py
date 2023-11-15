def ios_list_files(src, md5_hash, binary_form, mode):
    """List iOS files"""
    try:
        logger.info("Get Files, BIN Plist -> XML, and Normalize")
        # Multi function, Get Files, BIN Plist -> XML, normalize + to x
        filez = []
        certz = []
        sfiles = []
        database = []
        plist = []
        for dirname, _, files in os.walk(src):
            for jfile in files:
                if not jfile.endswith(".DS_Store"):
                    file_path = os.path.join(src, dirname, jfile)
                    if "+" in jfile:
                        plus2x = os.path.join(
                            src, dirname, jfile.replace("+", "x"))
                        shutil.move(file_path, plus2x)
                        file_path = plus2x
                    fileparam = file_path.replace(src, '')
                    filez.append(fileparam)
                    ext = jfile.split('.')[-1]
                    if re.search("cer|pem|cert|crt|pub|key|pfx|p12", ext):
                        certz.append({
                            'file_path': escape(file_path.replace(src, '')),
                            'type': None,
                            'hash': None
                        })

                    if re.search("db|sqlitedb|sqlite", ext):
                        database.append({
                            'file_path': escape(fileparam),
                            'type': mode,
                            'hash': md5_hash
                        })

                    if jfile.endswith(".plist"):
                        if binary_form:
                            convert_bin_xml(file_path)
                        plist.append({
                            'file_path': escape(fileparam),
                            'type': mode,
                            'hash': md5_hash
                        })

        if len(database) > 0:
            sfiles.append({"issue": "SQLite Files", "files": database})
        if len(plist) > 0:
            sfiles.append({"issue": "Plist Files", "files": plist})
        if len(certz) > 0:
            sfiles.append(
                {"issue": "Certificate/Key Files Hardcoded inside the App.", "files": certz})
        return filez, sfiles
    except:
        PrintException("[ERROR] iOS List Files")