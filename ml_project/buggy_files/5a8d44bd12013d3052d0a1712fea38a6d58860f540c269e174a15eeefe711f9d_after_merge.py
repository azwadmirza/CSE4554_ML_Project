def get_res():
    """Get Screen Resolution or Device or VM"""
    logger.info("Getting Screen Resolution")
    try:
        adb = getADB()
        resp = subprocess.check_output(
            [adb, "-s", get_identifier(), "shell", "dumpsys", "window"])
        resp = resp.decode("utf-8").split("\n")
        res = ""
        for line in resp:
            if "mUnrestrictedScreen" in line:
                res = line
                break
        res = res.split("(0,0)")[1]
        res = res.strip()
        res = res.split("x")
        if len(res) == 2:
            return res[0], res[1]
            # width, height
        return "", ""
    except:
        PrintException("Getting Screen Resolution")
        return "", ""