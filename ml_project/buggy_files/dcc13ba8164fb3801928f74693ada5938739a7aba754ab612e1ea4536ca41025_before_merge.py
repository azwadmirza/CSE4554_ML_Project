def create_db_tarball(args):
    tar = which('tar')
    tarball_name = "spack-db.%s.tar.gz" % _debug_tarball_suffix()
    tarball_path = os.path.abspath(tarball_name)

    with working_dir(spack.spack_root):
        files = [spack.installed_db._index_path]
        files += glob('%s/*/*/*/.spack/spec.yaml' % spack.install_path)
        files = [os.path.relpath(f) for f in files]

        tar('-czf', tarball_path, *files)

    tty.msg('Created %s' % tarball_name)