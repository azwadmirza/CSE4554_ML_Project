def admin_upgrade():
    """ Display any available upgrades and option to upgrade """
    if not utils_general.user_has_permission('edit_settings'):
        return redirect(url_for('routes_general.home'))

    misc = Misc.query.first()
    if not internet(host=misc.net_test_ip,
                    port=misc.net_test_port,
                    timeout=misc.net_test_timeout):
        return render_template('admin/upgrade.html',
                               is_internet=False)

    # Read from the upgrade status file created by the upgrade script
    # to indicate if the upgrade is running.
    try:
        with open(UPGRADE_INIT_FILE) as f:
            upgrade = int(f.read(1))
    except IOError:
        try:
            with open(UPGRADE_INIT_FILE, 'w') as f:
                f.write('0')
        finally:
            upgrade = 0

    if upgrade:
        if upgrade == 2:
            flash(gettext("There was an error encountered during the upgrade"
                          " process. Check the upgrade log for details."),
                  "error")
        return render_template('admin/upgrade.html',
                               current_release=MYCODO_VERSION,
                               upgrade=upgrade)

    form_backup = forms_misc.Backup()
    form_upgrade = forms_misc.Upgrade()

    is_internet = True
    upgrade_available = False

    # Check for any new Mycodo releases on github
    mycodo_releases = MycodoRelease()
    (upgrade_exists,
     releases,
     mycodo_releases,
     current_latest_release,
     errors) = mycodo_releases.github_upgrade_exists()

    if errors:
        for each_error in errors:
            flash(each_error, 'error')

    if releases:
        current_latest_major_version = current_latest_release.split('.')[0]
        current_major_release = releases[0]
        current_releases = []
        releases_behind = None
        for index, each_release in enumerate(releases):
            if parse_version(each_release) >= parse_version(MYCODO_VERSION):
                current_releases.append(each_release)
            if parse_version(each_release) == parse_version(MYCODO_VERSION):
                releases_behind = index
        if upgrade_exists:
            upgrade_available = True
    else:
        current_releases = []
        current_latest_major_version = '0'
        current_major_release = '0.0.0'
        releases_behind = 0

    # Update database to reflect the current upgrade status
    mod_misc = Misc.query.first()
    if mod_misc.mycodo_upgrade_available != upgrade_available:
        mod_misc.mycodo_upgrade_available = upgrade_available
        db.session.commit()

    def not_enough_space_upgrade():
        backup_size, free_before, free_after = can_perform_backup()
        if free_after / 1000000 < 50:
            flash(
                "A backup must be performed during an upgrade and there is "
                "not enough free space to perform a backup. A backup "
                "requires {size_bu:.1f} MB but there is only {size_free:.1f} "
                "MB available, which would leave {size_after:.1f} MB after "
                "the backup. If the free space after a backup is less than 50"
                " MB, the backup cannot proceed. Free up space by deleting "
                "current backups.".format(size_bu=backup_size / 1000000,
                                          size_free=free_before / 1000000,
                                          size_after=free_after / 1000000),
                'error')
            return True
        else:
            return False

    if request.method == 'POST':
        if (form_upgrade.upgrade.data and
                (upgrade_available or FORCE_UPGRADE_MASTER)):
            if not_enough_space_upgrade():
                pass
            elif FORCE_UPGRADE_MASTER:
                try:
                    os.remove(UPGRADE_TMP_LOG_FILE)
                except FileNotFoundError:
                    pass
                cmd = "{pth}/mycodo/scripts/mycodo_wrapper upgrade-master" \
                      " | ts '[%Y-%m-%d %H:%M:%S]' 2>&1 | tee -a {log} {tmp_log}".format(
                    pth=INSTALL_DIRECTORY,
                    log=UPGRADE_LOG_FILE,
                    tmp_log=UPGRADE_TMP_LOG_FILE)
                subprocess.Popen(cmd, shell=True)

                upgrade = 1
                flash(gettext("The upgrade (from master branch) has started"), "success")
            else:
                try:
                    os.remove(UPGRADE_TMP_LOG_FILE)
                except FileNotFoundError:
                    pass
                cmd = "{pth}/mycodo/scripts/mycodo_wrapper upgrade-release-major {current_maj_version}" \
                      " | ts '[%Y-%m-%d %H:%M:%S]' 2>&1 | tee -a {log} {tmp_log}".format(
                    current_maj_version=MYCODO_VERSION.split('.')[0],
                    pth=INSTALL_DIRECTORY,
                    log=UPGRADE_LOG_FILE,
                    tmp_log=UPGRADE_TMP_LOG_FILE)
                subprocess.Popen(cmd, shell=True)

                upgrade = 1
                mod_misc = Misc.query.first()
                mod_misc.mycodo_upgrade_available = False
                db.session.commit()
                flash(gettext("The upgrade has started"), "success")
        elif (form_upgrade.upgrade_next_major_version.data and
                upgrade_available):
            if not not_enough_space_upgrade():
                try:
                    os.remove(UPGRADE_TMP_LOG_FILE)
                except FileNotFoundError:
                    pass
                cmd = "{pth}/mycodo/scripts/mycodo_wrapper upgrade-release-wipe {ver}" \
                      " | ts '[%Y-%m-%d %H:%M:%S]' 2>&1 | tee -a {log} {tmp_log}".format(
                    pth=INSTALL_DIRECTORY,
                    ver=current_latest_major_version,
                    log=UPGRADE_LOG_FILE,
                    tmp_log=UPGRADE_TMP_LOG_FILE)
                subprocess.Popen(cmd, shell=True)

                upgrade = 1
                mod_misc = Misc.query.first()
                mod_misc.mycodo_upgrade_available = False
                db.session.commit()
                flash(gettext(
                    "The major version upgrade has started"), "success")
        else:
            flash(gettext(
                "You cannot upgrade if an upgrade is not available"),
                "error")

    return render_template('admin/upgrade.html',
                           final_releases=FINAL_RELEASES,
                           force_upgrade_master=FORCE_UPGRADE_MASTER,
                           form_backup=form_backup,
                           form_upgrade=form_upgrade,
                           current_release=MYCODO_VERSION,
                           current_releases=current_releases,
                           current_major_release=current_major_release,
                           current_latest_release=current_latest_release,
                           current_latest_major_version=current_latest_major_version,
                           releases_behind=releases_behind,
                           upgrade_available=upgrade_available,
                           upgrade=upgrade,
                           is_internet=is_internet)