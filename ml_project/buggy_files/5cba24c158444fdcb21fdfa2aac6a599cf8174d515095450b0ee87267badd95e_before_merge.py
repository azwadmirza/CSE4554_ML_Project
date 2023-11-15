  def _AttemptAutoDetectTagFile(self, analysis_mediator):
    """Detect which tag file is most appropriate.

    Args:
      analysis_mediator: The analysis mediator (Instance of
                         AnalysisMediator).

    Returns:
      True if a tag file is autodetected, False otherwise.
    """
    self._autodetect_tag_file_attempt = True
    platform = analysis_mediator.GetPlatform()
    filename = self._OS_TAG_FILES.get(platform.lower(), None)
    if not filename:
      return False
    tag_file_path = os.path.join(analysis_mediator.GetDataLocation(), filename)
    self.SetAndLoadTagFile(tag_file_path)
    return True