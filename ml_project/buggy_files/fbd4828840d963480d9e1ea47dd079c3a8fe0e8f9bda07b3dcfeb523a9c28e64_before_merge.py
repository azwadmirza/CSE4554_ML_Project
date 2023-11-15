  def _activate(self):
    self.update_candidate_distributions(self.load_internal_cache(self._pex, self._pex_info))

    if not self._pex_info.zip_safe and os.path.isfile(self._pex):
      self.update_module_paths(self.force_local(self._pex, self._pex_info))

    all_reqs = [Requirement.parse(req) for req in self._pex_info.requirements]

    working_set = WorkingSet([])
    resolved = self._resolve(working_set, all_reqs)

    for dist in resolved:
      with TRACER.timed('Activating %s' % dist, V=2):
        working_set.add(dist)

        if os.path.isdir(dist.location):
          with TRACER.timed('Adding sitedir', V=2):
            if dist.location not in sys.path and self._inherit_path == "fallback":
              # Prepend location to sys.path.
              # This ensures that bundled versions of libraries will be used before system-installed
              # versions, in case something is installed in both, helping to favor hermeticity in
              # the case of non-hermetic PEX files (i.e. those with inherit_path=True).
              #
              # If the path is not already in sys.path, site.addsitedir will append (not prepend)
              # the path to sys.path. But if the path is already in sys.path, site.addsitedir will
              # leave sys.path unmodified, but will do everything else it would do. This is not part
              # of its advertised contract (which is very vague), but has been verified to be the
              # case by inspecting its source for both cpython 2.7 and cpython 3.7.
              sys.path.insert(0, dist.location)
            site.addsitedir(dist.location)

        dist.activate()

    return working_set