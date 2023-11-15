def vendor_runtime(chroot, dest_basedir, label, root_module_names):
    """Includes portions of vendored distributions in a chroot.

    The portion to include is selected by root module name. If the module is a file, just it is
    included. If the module represents a package, the package and all its sub-packages are added
    recursively.

    :param chroot: The chroot to add vendored code to.
    :type chroot: :class:`pex.common.Chroot`
    :param str dest_basedir: The prefix to store the vendored code under in the ``chroot``.
    :param str label: The chroot label for the vendored code fileset.
    :param root_module_names: The names of the root vendored modules to include in the chroot.
    :type root_module_names: :class:`collections.Iterable` of str
    :raise: :class:`ValueError` if any of the given ``root_module_names`` could not be found amongst
            the vendored code and added to the chroot.
    """
    vendor_module_names = {root_module_name: False for root_module_name in root_module_names}
    for spec in iter_vendor_specs():
        for root, dirs, files in os.walk(spec.target_dir):
            if root == spec.target_dir:
                dirs[:] = [pkg_name for pkg_name in dirs if pkg_name in vendor_module_names]
                files[:] = [mod_name for mod_name in files if mod_name[:-3] in vendor_module_names]
                vendored_names = dirs + [filename[:-3] for filename in files]
                if vendored_names:
                    pkg_path = ""
                    for pkg in spec.relpath.split(os.sep):
                        pkg_path = os.path.join(pkg_path, pkg)
                        pkg_file = os.path.join(pkg_path, "__init__.py")
                        src = os.path.join(VendorSpec.ROOT, pkg_file)
                        dest = os.path.join(dest_basedir, pkg_file)
                        if os.path.exists(src):
                            chroot.copy(src, dest, label)
                        else:
                            # We delete `pex/vendor/_vendored/<dist>/__init__.py` when isolating third_party.
                            chroot.touch(dest, label)
                    for name in vendored_names:
                        vendor_module_names[name] = True
                        TRACER.log(
                            "Vendoring {} from {} @ {}".format(name, spec, spec.target_dir), V=3
                        )

            # We copy over sources and data only; no pyc files.
            dirs[:] = filter_pyc_dirs(dirs)
            for filename in filter_pyc_files(files):
                src = os.path.join(root, filename)
                dest = os.path.join(
                    dest_basedir, spec.relpath, os.path.relpath(src, spec.target_dir)
                )
                chroot.copy(src, dest, label)

    if not all(vendor_module_names.values()):
        raise ValueError(
            "Failed to extract {module_names} from:\n\t{specs}".format(
                module_names=", ".join(
                    module for module, written in vendor_module_names.items() if not written
                ),
                specs="\n\t".join(
                    "{} @ {}".format(spec, spec.target_dir) for spec in iter_vendor_specs()
                ),
            )
        )