def create_db_tarball(args):
    tar = which('tar')
    tarball_name = "spack-db.%s.tar.gz" % _debug_tarball_suffix()
    tarball_path = os.path.abspath(tarball_name)

    base = os.path.basename(spack.store.root)
    transform_args = []
    if 'GNU' in tar('--version', output=str):
        transform_args = ['--transform', 's/^%s/%s/' % (base, tarball_name)]
    else:
        transform_args = ['-s', '/^%s/%s/' % (base, tarball_name)]

    wd = os.path.dirname(spack.store.root)
    with working_dir(wd):
        files = [spack.store.db._index_path]
        files += glob('%s/*/*/*/.spack/spec.yaml' % base)
        files = [os.path.relpath(f) for f in files]

        args = ['-czf', tarball_path]
        args += transform_args
        args += files
        tar(*args)

    tty.msg('Created %s' % tarball_name)