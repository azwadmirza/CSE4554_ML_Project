  def install_vendored(cls, prefix, root=None, expose=None):
    """Install an importer for all vendored code with the given import prefix.

    All distributions listed in ``expose`` will also be made available for import in direct,
    un-prefixed form.

    :param str prefix: The import prefix the installed importer will be responsible for.
    :param str root: The root path of the distribution containing the vendored code. NB: This is the
                     the path to the pex code, which serves as the root under which code is vendored
                     at ``pex/vendor/_vendored``.
    :param expose: Optional names of distributions to expose for direct, un-prefixed import.
    :type expose: list of str
    :raise: :class:`ValueError` if any distributions to expose cannot be found.
    """
    from pex import vendor

    root = cls._abs_root(root)
    vendored_path_items = [spec.relpath for spec in vendor.iter_vendor_specs()]

    installed = list(cls._iter_installed_vendor_importers(prefix, root, vendored_path_items))
    assert len(installed) <= 1, (
      'Unexpected extra importers installed for vendored code:\n\t{}'
        .format('\n\t'.join(map(str, installed)))
    )
    if installed:
      vendor_importer = installed[0]
    else:
      # Install all vendored code for pex internal access to it through the vendor import `prefix`.
      vendor_importer = cls.install(uninstallable=True,
                                    prefix=prefix,
                                    path_items=vendored_path_items,
                                    root=root)

    if expose:
      # But only expose the bits needed.
      path_by_key = OrderedDict((spec.key, spec.relpath) for spec in vendor.iter_vendor_specs()
                                if spec.key in expose)
      path_by_key['pex'] = root  # The pex distribution itself is trivially available to expose.

      unexposed = set(expose) - set(path_by_key.keys())
      if unexposed:
        raise ValueError('The following vendored dists are not available to expose: {}'
                         .format(', '.join(sorted(unexposed))))

      exposed_paths = path_by_key.values()
      for exposed_path in exposed_paths:
        sys.path.insert(0, os.path.join(root, exposed_path))
      vendor_importer._expose(exposed_paths)