  def resolve(self, resolvables, resolvable_set=None):
    resolvables = [(resolvable, None) for resolvable in resolvables
                   if self.is_resolvable_in_target_interpreter_env(resolvable)]
    resolvable_set = resolvable_set or _ResolvableSet()
    processed_resolvables = set()
    processed_packages = {}
    distributions = {}

    while resolvables:
      while resolvables:
        resolvable, parent = resolvables.pop(0)
        if resolvable in processed_resolvables:
          continue
        packages = self.package_iterator(resolvable, existing=resolvable_set.get(resolvable.name))

        resolvable_set.merge(resolvable, packages, parent)
        processed_resolvables.add(resolvable)

      built_packages = {}
      for resolvable, packages, parent, constraint_only in resolvable_set.packages():
        if constraint_only:
          continue
        assert len(packages) > 0, 'ResolvableSet.packages(%s) should not be empty' % resolvable
        package = next(iter(packages))
        if resolvable.name in processed_packages:
          if package == processed_packages[resolvable.name]:
            continue
        if package not in distributions:
          dist = self.build(package, resolvable.options)
          built_package = Package.from_href(dist.location)
          built_packages[package] = built_package
          distributions[built_package] = dist
          package = built_package

        distribution = distributions[package]
        processed_packages[resolvable.name] = package
        new_parent = '%s->%s' % (parent, resolvable) if parent else str(resolvable)
        # We patch packaging.markers.default_environment here so we find optional reqs for the
        # platform we're building the PEX for, rather than the one we're on.
        with patched_packing_env(self._target_interpreter_env):
          resolvables.extend(
            (ResolvableRequirement(req, resolvable.options), new_parent) for req in
            distribution.requires(extras=resolvable_set.extras(resolvable.name))
          )
      resolvable_set = resolvable_set.replace_built(built_packages)

    # We may have built multiple distributions depending upon if we found transitive dependencies
    # for the same package. But ultimately, resolvable_set.packages() contains the correct version
    # for all packages. So loop through it and only return the package version in
    # resolvable_set.packages() that is found in distributions.
    dists = []
    # No point in proceeding if distributions is empty
    if not distributions:
      return dists

    for resolvable, packages, parent, constraint_only in resolvable_set.packages():
      if constraint_only:
        continue
      assert len(packages) > 0, 'ResolvableSet.packages(%s) should not be empty' % resolvable
      package = next(iter(packages))
      distribution = distributions[package]
      if isinstance(resolvable, ResolvableRequirement):
        requirement = resolvable.requirement
      else:
        requirement = distribution.as_requirement()
        requirement.extras = tuple(resolvable.extras())
      dists.append(ResolvedDistribution(requirement=requirement,
                                        distribution=distribution))
    return dists