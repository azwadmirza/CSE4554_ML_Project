  def cache_distribution(cls, zf, source, target_dir):
    """Possibly cache an egg from within a zipfile into target_cache.

       Given a zipfile handle and a filename corresponding to an egg distribution within
       that zip, maybe write to the target cache and return a Distribution."""
    dependency_basename = os.path.basename(source)
    if not os.path.exists(target_dir):
      target_dir_tmp = target_dir + '.' + uuid.uuid4().hex
      for name in zf.namelist():
        if name.startswith(source) and not name.endswith('/'):
          # strip off prefix + '/'
          target_name = os.path.join(dependency_basename, name[len(source) + 1:])
          with contextlib.closing(zf.open(name)) as zi:
            with safe_open(os.path.join(target_dir_tmp, target_name), 'wb') as fp:
              shutil.copyfileobj(zi, fp)
      try:
        os.rename(target_dir_tmp, target_dir)
      except OSError as e:
        if e.errno == errno.ENOTEMPTY:
          safe_rmtree(target_dir_tmp)
        else:
          raise

    dist = DistributionHelper.distribution_from_path(target_dir)
    assert dist is not None, 'Failed to cache distribution %s' % source
    return dist