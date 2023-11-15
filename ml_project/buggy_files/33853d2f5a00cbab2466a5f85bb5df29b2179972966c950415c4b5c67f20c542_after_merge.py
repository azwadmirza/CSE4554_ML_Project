def download(md5_hash, download_dir, apk_dir, package):
    """Generating Downloads"""
    logger.info("Generating Downloads")
    try:

        capfuzz_home = os.path.join(str(Path.home()), ".capfuzz")
        logcat = os.path.join(apk_dir, 'logcat.txt')
        xlogcat = os.path.join(apk_dir, 'x_logcat.txt')
        dumpsys = os.path.join(apk_dir, 'dump.txt')
        sshot = os.path.join(apk_dir, 'screenshots-apk/')
        web = os.path.join(capfuzz_home, 'flows', package + ".flows.txt")
        star = os.path.join(apk_dir, package + '.tar')

        dlogcat = os.path.join(download_dir, md5_hash + '-logcat.txt')
        dxlogcat = os.path.join(download_dir, md5_hash + '-x_logcat.txt')
        ddumpsys = os.path.join(download_dir, md5_hash + '-dump.txt')
        dsshot = os.path.join(download_dir, md5_hash + '-screenshots-apk/')
        dweb = os.path.join(download_dir, md5_hash + '-WebTraffic.txt')
        dstar = os.path.join(download_dir, md5_hash + '-AppData.tar')

        # Delete existing data
        dellist = [dlogcat, dxlogcat, ddumpsys, dsshot, dweb, dstar]
        for item in dellist:
            if os.path.isdir(item):
                shutil.rmtree(item)
            elif os.path.isfile(item):
                os.remove(item)
        # Copy new data
        shutil.copyfile(logcat, dlogcat)
        shutil.copyfile(xlogcat, dxlogcat)
        shutil.copyfile(dumpsys, ddumpsys)
        try:
            shutil.copytree(sshot, dsshot)
        except:
            pass
        try:
            shutil.copyfile(web, dweb)
        except:
            pass
        try:
            shutil.copyfile(star, dstar)
        except:
            pass
    except:
        PrintException("Generating Downloads")