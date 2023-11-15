  def _get_extra_function_args(self, state, arg):
    """Get function annotations and defaults from the stack. (Python3.5-)."""
    if self.PY2:
      num_pos_defaults = arg & 0xffff
      num_kw_defaults = 0
    else:
      assert self.PY3
      num_pos_defaults = arg & 0xff
      num_kw_defaults = (arg >> 8) & 0xff
    state, raw_annotations = state.popn((arg >> 16) & 0x7fff)
    state, kw_defaults = state.popn(2 * num_kw_defaults)
    state, pos_defaults = state.popn(num_pos_defaults)
    free_vars = None  # Python < 3.6 does not handle closure vars here.
    kw_defaults = self._convert_kw_defaults(kw_defaults)
    annot = self.annotations_util.convert_function_annotations(
        state.node, raw_annotations)
    return state, pos_defaults, kw_defaults, annot, free_vars