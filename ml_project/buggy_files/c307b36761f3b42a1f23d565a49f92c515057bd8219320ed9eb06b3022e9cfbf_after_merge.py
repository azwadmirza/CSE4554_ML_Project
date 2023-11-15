  def requires(package, requirement):
    if not distributions.has(package):
      with TRACER.timed('Fetching %s' % package.url, V=2):
        local_package = Package.from_href(context.fetch(package, into=cache))
      if package.remote:
        # this was a remote resolution -- so if we copy from remote to local but the
        # local already existed, update the mtime of the local so that it is correct
        # with respect to cache_ttl.
        os.utime(local_package.path, None)
      with TRACER.timed('Translating %s into distribution' % local_package.path, V=2):
        dist = translator.translate(local_package, into=cache)
      if dist is None:
        raise Untranslateable('Package %s is not translateable.' % package)
      if not distribution_compatible(dist, interpreter, platform):
        raise Untranslateable('Could not get distribution for %s on appropriate platform.' %
            package)
      distributions.put(package, dist)
    dist = distributions.get(package)
    return dist.requires(extras=requirement.extras)