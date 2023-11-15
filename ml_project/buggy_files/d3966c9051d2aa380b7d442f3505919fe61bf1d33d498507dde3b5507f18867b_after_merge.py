  def expose(cls, dists, root=None):
    from pex import vendor

    root = cls._abs_root(root)

    def iter_available():
      yield 'pex', root  # The pex distribution itself is trivially available to expose.
      for spec in vendor.iter_vendor_specs():
        yield spec.key, spec.relpath

    path_by_key = OrderedDict((key, relpath) for key, relpath in iter_available() if key in dists)

    unexposed = set(dists) - set(path_by_key.keys())
    if unexposed:
      raise ValueError('The following vendored dists are not available to expose: {}'
                       .format(', '.join(sorted(unexposed))))

    exposed_paths = path_by_key.values()
    for exposed_path in exposed_paths:
      yield os.path.join(root, exposed_path)