def get_buildroot():
  """Returns the pants build root, calculating it if needed.

  :API: public
  """
  return BuildRoot().path