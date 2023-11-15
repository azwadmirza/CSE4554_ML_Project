def GetParsersFromCategory(category):
  """Return a list of parsers from a parser category."""
  return_list = []
  if category not in categories:
    return return_list

  for item in categories.get(category):
    if item in categories:
      return_list.extend(GetParsersFromCategory(item))
    else:
      return_list.append(item)

  return return_list