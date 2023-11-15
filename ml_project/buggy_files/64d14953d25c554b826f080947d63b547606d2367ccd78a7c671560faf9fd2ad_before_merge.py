def replace_directory_transaction(directory_name, tmp_root=None):
    """Moves a directory to a temporary space. If the operations executed
    within the context manager don't raise an exception, the directory is
    deleted. If there is an exception, the move is undone.

    Args:
        directory_name (path): absolute path of the directory name
        tmp_root (path): absolute path of the parent directory where to create
            the temporary

    Returns:
        temporary directory where ``directory_name`` has been moved
    """
    # Check the input is indeed a directory with absolute path.
    # Raise before anything is done to avoid moving the wrong directory
    assert os.path.isdir(directory_name), \
        '"directory_name" must be a valid directory'
    assert os.path.isabs(directory_name), \
        '"directory_name" must contain an absolute path'

    directory_basename = os.path.basename(directory_name)

    if tmp_root is not None:
        assert os.path.isabs(tmp_root)

    tmp_dir = tempfile.mkdtemp(dir=tmp_root)
    tty.debug('TEMPORARY DIRECTORY CREATED [{0}]'.format(tmp_dir))

    shutil.move(src=directory_name, dst=tmp_dir)
    tty.debug('DIRECTORY MOVED [src={0}, dest={1}]'.format(
        directory_name, tmp_dir
    ))

    try:
        yield tmp_dir
    except (Exception, KeyboardInterrupt, SystemExit):
        # Delete what was there, before copying back the original content
        if os.path.exists(directory_name):
            shutil.rmtree(directory_name)
        shutil.move(
            src=os.path.join(tmp_dir, directory_basename),
            dst=os.path.dirname(directory_name)
        )
        tty.debug('DIRECTORY RECOVERED [{0}]'.format(directory_name))

        msg = 'the transactional move of "{0}" failed.'
        raise RuntimeError(msg.format(directory_name))
    else:
        # Otherwise delete the temporary directory
        shutil.rmtree(tmp_dir)
        tty.debug('TEMPORARY DIRECTORY DELETED [{0}]'.format(tmp_dir))