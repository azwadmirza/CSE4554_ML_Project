def result_type(*args):
  """Convenience function to apply Numpy argument dtype promotion."""
  if len(args) == 0:
    raise ValueError("at least one array or dtype is required")
  return canonicalize_dtype(_result_type_raw(*args))