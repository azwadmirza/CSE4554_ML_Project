def extract(dist):
    """
    Extract a package, i.e. make a package available for linkage. We assume
    that the compressed package is located in the packages directory.
    """
    rec = package_cache()[dist]
    url = rec['urls'][0]
    fname = rec['files'][0]
    assert url and fname
    pkgs_dir = dirname(fname)
    with Locked(pkgs_dir):
        path = fname[:-8]
        temp_path = path + '.tmp'
        rm_rf(temp_path)
        with tarfile.open(fname) as t:
            t.extractall(path=temp_path)
        rm_rf(path)
        os.rename(temp_path, path)
        if sys.platform.startswith('linux') and os.getuid() == 0:
            # When extracting as root, tarfile will by restore ownership
            # of extracted files.  However, we want root to be the owner
            # (our implementation of --no-same-owner).
            for root, dirs, files in os.walk(path):
                for fn in files:
                    p = join(root, fn)
                    os.lchown(p, 0, 0)
        add_cached_package(pkgs_dir, url, overwrite=True)