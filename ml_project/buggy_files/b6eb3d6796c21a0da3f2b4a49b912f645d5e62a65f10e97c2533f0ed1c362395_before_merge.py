def result_type(*args):
  """Convenience function to apply Numpy argument dtype promotion."""
  return canonicalize_dtype(_result_type_raw(*args))