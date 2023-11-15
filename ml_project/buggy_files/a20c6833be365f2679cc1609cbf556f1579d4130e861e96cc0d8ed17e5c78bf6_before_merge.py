  def _GetSectionNames(self, pefile_object):
    """Retrieves all PE section names.

    Args:
      pefile_object: The pefile object to get the names from
        (instance of pefile.PE).

    Returns:
      A list of the names of the sections.
    """
    section_names = []
    for section in pefile_object.sections:
      section_names.append(getattr(section, u'Name', None))
    return section_names