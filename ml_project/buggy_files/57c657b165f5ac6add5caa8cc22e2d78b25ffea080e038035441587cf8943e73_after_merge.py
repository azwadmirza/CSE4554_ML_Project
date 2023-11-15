  def _get_extra_function_args_3_6(self, state, arg):
    """Get function annotations and defaults from the stack (Python3.6+)."""
    free_vars = None
    pos_defaults = ()
    kw_defaults = {}
    annot = {}
    if arg & loadmarshal.MAKE_FUNCTION_HAS_FREE_VARS:
      state, free_vars = state.pop()
    if arg & loadmarshal.MAKE_FUNCTION_HAS_ANNOTATIONS:
      state, packed_annot = state.pop()
      annot = abstract_utils.get_atomic_python_constant(packed_annot, dict)
      for k in annot.keys():
        annot[k] = self.annotations_util.convert_function_type_annotation(
            k, annot[k])
    if arg & loadmarshal.MAKE_FUNCTION_HAS_KW_DEFAULTS:
      state, packed_kw_def = state.pop()
      kw_defaults = abstract_utils.get_atomic_python_constant(
          packed_kw_def, dict)
    if arg & loadmarshal.MAKE_FUNCTION_HAS_POS_DEFAULTS:
      state, packed_pos_def = state.pop()
      pos_defaults = abstract_utils.get_atomic_python_constant(
          packed_pos_def, tuple)
    annot = self.annotations_util.convert_annotations_list(
        state.node, annot.items())
    return state, pos_defaults, kw_defaults, annot, free_vars