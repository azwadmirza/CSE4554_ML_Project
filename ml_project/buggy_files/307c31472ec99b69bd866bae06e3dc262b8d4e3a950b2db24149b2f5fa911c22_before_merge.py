def query_virtual(module, name):
    cmd = "%s -v info --description %s" % (APK_PATH, name)
    rc, stdout, stderr = module.run_command(cmd, check_rc=False)
    search_pattern = "^%s: virtual meta package" % (name)
    if re.search(search_pattern, stdout):
        return True
    return False