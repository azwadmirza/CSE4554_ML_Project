  def trace_opcode(self, op, symbol, val):
    """Record trace data for other tools to use."""
    if not self._trace_opcodes:
      return

    if self.frame and not op:
      op = self.frame.current_opcode
    if not op:
      # If we don't have a current opcode, don't emit a trace.
      return

    def get_data(v):
      data = getattr(v, "data", None)
      # Sometimes v is a binding.
      return [data] if data and not isinstance(data, list) else data

    # isinstance(val, tuple) generates false positives for internal classes like
    # LateAnnotations that are namedtuples.
    if val.__class__ == tuple:
      data = tuple(get_data(v) for v in val)
    else:
      data = (get_data(val),)
    rec = (op, symbol, data)
    self.opcode_traces.append(rec)