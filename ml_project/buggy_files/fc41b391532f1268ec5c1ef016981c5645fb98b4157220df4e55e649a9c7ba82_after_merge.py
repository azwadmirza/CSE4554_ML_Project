def check_update():
    try:
        logger.info("Checking for Update.")
        github_url = "https://raw.githubusercontent.com/MobSF/Mobile-Security-Framework-MobSF/master/MobSF/settings.py"
        try:
            proxies, verify = upstream_proxy('https')
        except Exception:
            PrintException("Setting upstream proxy")
        response = requests.get(github_url, timeout=5,
                                proxies=proxies, verify=verify)
        html = str(response.text).split("\n")
        for line in html:
            if line.startswith("MOBSF_VER"):
                line = line.replace("MOBSF_VER", "").replace('"', '')
                line = line.replace("=", "").strip()
                if line != settings.MOBSF_VER:
                    logger.warning("A new version of MobSF is available, Please update from master branch or check "
                                   "for new releases.")
                else:
                    logger.info("No updates available.")
    except requests.exceptions.HTTPError as err:
        logger.warning(
            "\nCannot check for updates.. No Internet Connection Found.")
        return
    except:
        PrintException("Cannot Check for updates.")