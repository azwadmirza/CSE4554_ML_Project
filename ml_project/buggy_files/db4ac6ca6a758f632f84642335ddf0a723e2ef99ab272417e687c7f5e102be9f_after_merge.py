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
      section_name = getattr(section, u'Name', b'')
      # Ensure the name is decoded correctly.
      try:
        section_name = u'{0:s}'.format(section_name.decode(u'unicode_escape'))
      except UnicodeDecodeError:
        section_name = u'{0:s}'.format(repr(section_name))
      section_names.append(section_name)

    return section_names