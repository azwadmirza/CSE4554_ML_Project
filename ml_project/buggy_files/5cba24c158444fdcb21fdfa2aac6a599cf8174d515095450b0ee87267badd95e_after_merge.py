  def _AttemptAutoDetectTagFile(self, analysis_mediator):
    """Detect which tag file is most appropriate.

    Args:
      analysis_mediator: The analysis mediator (Instance of
                         AnalysisMediator).

    Returns:
      True if a tag file is autodetected, False otherwise.
    """
    self._autodetect_tag_file_attempt = True
    if not analysis_mediator.data_location:
      return False
    platform = analysis_mediator.platform
    filename = self._OS_TAG_FILES.get(platform.lower(), None)
    if not filename:
      return False
    logging.info(u'Using auto detected tag file: {0:s}'.format(filename))
    tag_file_path = os.path.join(analysis_mediator.data_location, filename)
    self.SetAndLoadTagFile(tag_file_path)
    return True