def upgrade_packages(module):
    if module.check_mode:
        cmd = "%s upgrade --simulate" % (APK_PATH)
    else:
        cmd = "%s upgrade" % (APK_PATH)
    rc, stdout, stderr = module.run_command(cmd, check_rc=False)
    if rc != 0:
        module.fail_json(msg="failed to upgrade packages")
    if re.search('^OK', stdout):
        module.exit_json(changed=False, msg="packages already upgraded")
    module.exit_json(changed=True, msg="upgraded packages")