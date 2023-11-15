def unzip(app_path, ext_path):
    logger.info("Unzipping")
    try:
        files = []
        with zipfile.ZipFile(app_path, "r") as zipptr:
            for fileinfo in zipptr.infolist():
                filename = fileinfo.filename
                if not isinstance(filename, str):
                    filename = str(
                        filename, encoding="utf-8", errors="replace")
                files.append(filename)
                zipptr.extract(filename, ext_path)
        return files
    except:
        PrintException("[ERROR] Unzipping Error")
        if platform.system() == "Windows":
            logger.info("Not yet Implemented.")
        else:
            logger.info("Using the Default OS Unzip Utility.")
            try:
                subprocess.call(
                    ['unzip', '-o', '-I utf-8', '-q', app_path, '-d', ext_path])
                dat = subprocess.check_output(['unzip', '-qq', '-l', app_path])
                dat = dat.decode('utf-8').split('\n')
                files_det = ['Length   Date   Time   Name']
                files_det = files_det + dat
                return files_det
            except:
                PrintException("[ERROR] Unzipping Error")