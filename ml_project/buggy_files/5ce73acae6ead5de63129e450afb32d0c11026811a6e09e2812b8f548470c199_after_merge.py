def _copy_dist_from_dir(link_path, location):
    """Copy distribution files in `link_path` to `location`.

    Invoked when user requests to install a local directory. E.g.:

        pip install .
        pip install ~/dev/git-repos/python-prompt-toolkit

    """

    # Note: This is currently VERY SLOW if you have a lot of data in the
    # directory, because it copies everything with `shutil.copytree`.
    # What it should really do is build an sdist and install that.
    # See https://github.com/pypa/pip/issues/2195

    if os.path.isdir(location):
        rmtree(location)

    # build an sdist
    setup_py = 'setup.py'
    sdist_args = [sys.executable]
    sdist_args.append('-c')
    sdist_args.append(SETUPTOOLS_SHIM % setup_py)
    sdist_args.append('sdist')
    sdist_args += ['--dist-dir', location]
    logger.info('Running setup.py sdist for %s', link_path)

    with indent_log():
        call_subprocess(sdist_args, cwd=link_path, show_stdout=False)

    # unpack sdist into `location`
    sdist = os.path.join(location, os.listdir(location)[0])
    logger.info('Unpacking sdist %s into %s', sdist, location)
    unpack_file(sdist, location, content_type=None, link=None)