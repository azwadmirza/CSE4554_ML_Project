def packages_from_requirement_cached(local_iterator, ttl, iterator, requirement, *args, **kw):
  packages = packages_from_requirement(local_iterator, requirement, *args, **kw)

  if packages:
    # match with exact requirement, always accept.
    if requirement_is_exact(requirement):
      TRACER.log('Package cache hit: %s' % requirement, V=3)
      return packages

    # match with inexact requirement, consider if ttl supplied.
    if ttl:
      now = time.time()
      packages = [package for package in packages if (now - os.path.getmtime(package.path)) < ttl]
      if packages:
        TRACER.log('Package cache hit (inexact): %s' % requirement, V=3)
        return packages

  # no matches in the local cache
  TRACER.log('Package cache miss: %s' % requirement, V=3)
  return packages_from_requirement(iterator, requirement, *args, **kw)