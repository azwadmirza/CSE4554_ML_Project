def ensure(module, base, state, names):
    allow_erasing = False
    if names == ['*'] and state == 'latest':
        base.upgrade_all()
    else:
        pkg_specs, group_specs, filenames = dnf.cli.commands.parse_spec_group_file(
            names)
        if group_specs:
            base.read_comps()

        groups = []
        for group_spec in group_specs:
            group = base.comps.group_by_pattern(group_spec)
            if group:
                groups.append(group)
            else:
                module.fail_json(
                    msg="No group {} available.".format(group_spec))

        if state in ['installed', 'present']:
            # Install files.
            for filename in filenames:
                base.package_install(base.add_remote_rpm(filename))
            # Install groups.
            for group in groups:
                base.group_install(group, dnf.const.GROUP_PACKAGE_TYPES)
            # Install packages.
            for pkg_spec in pkg_specs:
                _mark_package_install(module, base, pkg_spec)

        elif state == 'latest':
            # "latest" is same as "installed" for filenames.
            for filename in filenames:
                base.package_install(base.add_remote_rpm(filename))
            for group in groups:
                try:
                    base.group_upgrade(group)
                except dnf.exceptions.CompsError:
                    # If not already installed, try to install.
                    base.group_install(group, dnf.const.GROUP_PACKAGE_TYPES)
            for pkg_spec in pkg_specs:
                # best effort causes to install the latest package
                # even if not previously installed
                base.conf.best = True
                base.install(pkg_spec)

        else:
            # state == absent
            if filenames:
                module.fail_json(
                    msg="Cannot remove paths -- please specify package name.")

            installed = base.sack.query().installed()
            for group in groups:
                if installed.filter(name=group.name):
                    base.group_remove(group)
            for pkg_spec in pkg_specs:
                if installed.filter(name=pkg_spec):
                    base.remove(pkg_spec)
            # Like the dnf CLI we want to allow recursive removal of dependent
            # packages
            allow_erasing = True

    if not base.resolve(allow_erasing=allow_erasing):
        module.exit_json(msg="Nothing to do")
    else:
        if module.check_mode:
            module.exit_json(changed=True)
        base.download_packages(base.transaction.install_set)
        base.do_transaction()
        response = {'changed': True, 'results': []}
        for package in base.transaction.install_set:
            response['results'].append("Installed: {}".format(package))
        for package in base.transaction.remove_set:
            response['results'].append("Removed: {}".format(package))

        module.exit_json(**response)