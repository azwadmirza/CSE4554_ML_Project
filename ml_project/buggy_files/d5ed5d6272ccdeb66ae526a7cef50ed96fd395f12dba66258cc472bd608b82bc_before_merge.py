  def _ParsePathSpecification(
      self, knowledge_base, searcher, file_system, path_specification,
      path_separator):
    """Parses a file system for a preprocessing attribute.

    Args:
      knowledge_base (KnowledgeBase): to fill with preprocessing information.
      searcher (dfvfs.FileSystemSearcher): file system searcher to preprocess
          the file system.
      file_system (dfvfs.FileSystem): file system to be preprocessed.
      path_specification (dfvfs.PathSpec): path specification that contains
          the artifact value data.
      path_separator (str): path segment separator.

    Raises:
      PreProcessFail: if the preprocessing fails.
    """
    try:
      file_entry = searcher.GetFileEntryByPathSpec(path_specification)
    except IOError as exception:
      relative_path = searcher.GetRelativePath(path_specification)
      if path_separator != file_system.PATH_SEPARATOR:
        relative_path_segments = file_system.SplitPath(relative_path)
        relative_path = '{0:s}{1:s}'.format(
            path_separator, path_separator.join(relative_path_segments))

      raise errors.PreProcessFail((
          'Unable to retrieve file entry: {0:s} with error: '
          '{1!s}').format(relative_path, exception))

    self._ParseFileEntry(knowledge_base, file_entry)