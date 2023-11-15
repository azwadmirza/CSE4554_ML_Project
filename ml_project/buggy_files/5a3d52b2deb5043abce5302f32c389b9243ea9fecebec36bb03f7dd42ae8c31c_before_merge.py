  def CopyToDict(self):
    """Copies the attribute container to a dictionary.

    Returns:
      dict[str, object]: attribute values per name.
    """
    return {
        attribute_name: attribute_value
        for attribute_name, attribute_value in self.GetAttributes()}