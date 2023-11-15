def _get_frame_info(stacklevel: int, context: int = 1) -> inspect.FrameInfo:
  """Get a Traceback for the given `stacklevel`.

  For example:
  `stacklevel=0` means this function's frame (_get_frame_info()).
  `stacklevel=1` means the calling function's frame.
  See https://docs.python.org/2/library/inspect.html#inspect.getouterframes for more info.

  NB: If `stacklevel` is greater than the number of actual frames, the outermost frame is used
  instead.
  """
  frame_list = inspect.getouterframes(inspect.currentframe(), context=context)
  frame_stack_index = stacklevel if stacklevel < len(frame_list) else len(frame_list) - 1
  return frame_list[frame_stack_index]