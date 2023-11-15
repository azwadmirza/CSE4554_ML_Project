  def AddAnalysisReport(self, analysis_report):
    """Adds an analysis report.

    Args:
      analysis_report: an analysis report object (instance of AnalysisReport).

    Raises:
      IOError: when the storage writer is closed.
    """
    if not self._storage_file:
      raise IOError(u'Unable to write to closed storage writer.')

    for event_tag in analysis_report.GetTags():
      self.AddEventTag(event_tag)

    self._storage_file.AddAnalysisReport(analysis_report)

    report_identifier = analysis_report.plugin_name
    self._session.analysis_reports_counter[u'total'] += 1
    self._session.analysis_reports_counter[report_identifier] += 1
    self.number_of_analysis_reports += 1