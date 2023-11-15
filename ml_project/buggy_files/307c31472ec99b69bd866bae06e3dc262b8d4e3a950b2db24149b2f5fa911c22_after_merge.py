def query_virtual(module, name):
    cmd = "%s -v info --description %s" % (APK_PATH, name)
    rc, stdout, stderr = module.run_command(cmd, check_rc=False)
    search_pattern = r"^%s: virtual meta package" % (re.escape(name))
    if re.search(search_pattern, stdout):
        return True
    return False