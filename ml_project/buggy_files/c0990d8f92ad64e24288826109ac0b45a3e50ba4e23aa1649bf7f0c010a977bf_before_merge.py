def setup_package():

    # Perform 2to3 if needed
    local_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    src_path = local_path

    if sys.version_info[0] == 3:
        src_path = os.path.join(local_path, 'build', 'py3k')
        sys.path.insert(0, os.path.join(local_path, 'tools'))
        import py3tool
        print("Converting to Python3 via 2to3...")
        py3tool.sync_2to3('numpy', os.path.join(src_path, 'numpy'))

        site_cfg = os.path.join(local_path, 'site.cfg')
        if os.path.isfile(site_cfg):
            shutil.copy(site_cfg, src_path)

    old_path = os.getcwd()
    os.chdir(src_path)
    sys.path.insert(0, src_path)

    # Rewrite the version file everytime
    write_version_py()

    # Run build
    from numpy.distutils.core import setup

    try:
        setup(
            name=NAME,
            maintainer=MAINTAINER,
            maintainer_email=MAINTAINER_EMAIL,
            description=DESCRIPTION,
            long_description=LONG_DESCRIPTION,
            url=URL,
            download_url=DOWNLOAD_URL,
            license=LICENSE,
            classifiers=CLASSIFIERS,
            author=AUTHOR,
            author_email=AUTHOR_EMAIL,
            platforms=PLATFORMS,
            configuration=configuration )
    finally:
        del sys.path[0]
        os.chdir(old_path)
    return