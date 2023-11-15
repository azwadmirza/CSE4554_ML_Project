def get_buildroot():
  """Returns the pants build root, calculating it if needed.

  :API: public
  """
  try:
    return BuildRoot().path
  except BuildRoot.NotFoundError as e:
    print(str(e), file=sys.stderr)
    sys.exit(1)