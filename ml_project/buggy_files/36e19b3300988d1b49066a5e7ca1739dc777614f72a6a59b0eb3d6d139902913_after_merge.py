  def simple_stack(self, opcode=None):
    """Get a stack of simple frames.

    Args:
      opcode: Optionally, an opcode to create a stack for.

    Returns:
      If an opcode is provided, a stack with a single frame at that opcode.
      Otherwise, the VM's current stack converted to simple frames.
    """
    if opcode is not None:
      return (frame_state.SimpleFrame(opcode),)
    elif self.frame:
      # Simple stacks are used for things like late annotations, which don't
      # need tracebacks in their errors, so we convert just the current frame.
      return (frame_state.SimpleFrame(self.frame.current_opcode),)
    else:
      return ()