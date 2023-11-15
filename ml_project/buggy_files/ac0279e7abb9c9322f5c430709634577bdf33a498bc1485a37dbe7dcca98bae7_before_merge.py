def bundle():
    clean()

    if MACOS:
        patch_dmgbuild()

    # smoke test, and build resources
    subprocess.check_call([sys.executable, '-m', APP, '--info'])
    patch_toml()

    # create
    cmd = ['briefcase', 'create'] + (['--no-docker'] if LINUX else [])
    subprocess.check_call(cmd)

    time.sleep(0.5)

    add_site_packages_to_path()

    if WINDOWS:
        patch_wxs()

    # build
    cmd = ['briefcase', 'build'] + (['--no-docker'] if LINUX else [])
    subprocess.check_call(cmd)

    # package
    cmd = ['briefcase', 'package']
    cmd += ['--no-sign'] if MACOS else (['--no-docker'] if LINUX else [])
    subprocess.check_call(cmd)

    # compress
    dest = make_zip()
    clean()

    with open(PYPROJECT_TOML, 'w') as f:
        f.write(original_toml)

    return dest