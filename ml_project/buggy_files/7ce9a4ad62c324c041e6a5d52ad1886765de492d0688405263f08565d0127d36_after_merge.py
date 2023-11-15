def isolated():
    """Returns a chroot for third_party isolated from the ``sys.path``.

    PEX will typically be installed in site-packages flat alongside many other distributions; as such,
    adding the location of the pex distribution to the ``sys.path`` will typically expose many other
    distributions. An isolated chroot can be used as a ``sys.path`` entry to effect only the exposure
    of pex.

    :return: An isolation result.
    :rtype: :class:`IsolationResult`
    """
    global _ISOLATED
    if _ISOLATED is None:
        from pex import vendor
        from pex.common import atomic_directory
        from pex.util import CacheHelper
        from pex.variables import ENV
        from pex.third_party.pkg_resources import resource_isdir, resource_listdir, resource_stream

        module = "pex"

        # TODO(John Sirois): Unify with `pex.util.DistributionHelper.access_zipped_assets`.
        def recursive_copy(srcdir, dstdir):
            os.mkdir(dstdir)
            for entry_name in resource_listdir(module, srcdir):
                if not entry_name:
                    # The `resource_listdir` function returns a '' entry name for the directory
                    # entry itself if it is either present on the filesystem or present as an
                    # explicit zip entry. Since we only care about files and subdirectories at this
                    # point, skip these entries.
                    continue
                # NB: Resource path components are always separated by /, on all systems.
                src_entry = "{}/{}".format(srcdir, entry_name) if srcdir else entry_name
                dst_entry = os.path.join(dstdir, entry_name)
                if resource_isdir(module, src_entry):
                    recursive_copy(src_entry, dst_entry)
                elif not entry_name.endswith(".pyc"):
                    with open(dst_entry, "wb") as fp:
                        with closing(resource_stream(module, src_entry)) as resource:
                            shutil.copyfileobj(resource, fp)

        pex_path = os.path.join(vendor.VendorSpec.ROOT, "pex")
        with _tracer().timed("Hashing pex"):
            dir_hash = CacheHelper.dir_hash(pex_path)
        isolated_dir = os.path.join(ENV.PEX_ROOT, "isolated", dir_hash)

        with _tracer().timed("Isolating pex"):
            with atomic_directory(isolated_dir, exclusive=True) as chroot:
                if chroot:
                    with _tracer().timed("Extracting pex to {}".format(isolated_dir)):
                        recursive_copy("", os.path.join(chroot, "pex"))

        _ISOLATED = IsolationResult(pex_hash=dir_hash, chroot_path=isolated_dir)
    return _ISOLATED