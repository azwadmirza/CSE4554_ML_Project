  def execute(self):
    # NB: Downstream product consumers may need the selected interpreter for use with
    # any type of importable Python target, including `PythonRequirementLibrary` targets
    # (for use with the `repl` goal, for instance). For interpreter selection,
    # we only care about targets with compatibility constraints.
    python_tgts_and_reqs = self.context.targets(
      lambda tgt: isinstance(tgt, (PythonTarget, PythonRequirementLibrary))
    )
    if not python_tgts_and_reqs:
      return
    python_tgts = [tgt for tgt in python_tgts_and_reqs if isinstance(tgt, PythonTarget)]
    fs = PythonInterpreterFingerprintStrategy()
    with self.invalidated(python_tgts, fingerprint_strategy=fs) as invalidation_check:
      # If there are no relevant targets, we still go through the motions of selecting
      # an interpreter, to prevent downstream tasks from having to check for this special case.
      if invalidation_check.all_vts:
        target_set_id = VersionedTargetSet.from_versioned_targets(
            invalidation_check.all_vts).cache_key.hash
      else:
        target_set_id = 'no_targets'
      interpreter_path_file = self._interpreter_path_file(target_set_id)
      if not os.path.exists(interpreter_path_file):
        self._create_interpreter_path_file(interpreter_path_file, python_tgts)

    interpreter = self._get_interpreter(interpreter_path_file)
    self.context.products.register_data(PythonInterpreter, interpreter)