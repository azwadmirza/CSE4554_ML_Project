  def ProduceAnalysisReport(self, plugin):
    """Produces an analysis report.

    Args:
      plugin (AnalysisPlugin): plugin.
    """
    analysis_report = plugin.CompileReport(self)
    if not analysis_report:
      return

    analysis_report.time_compiled = timelib.Timestamp.GetNow()

    plugin_name = getattr(analysis_report, u'plugin_name', plugin.plugin_name)
    if plugin_name:
      analysis_report.plugin_name = plugin_name

    if self._event_filter_expression:
      # TODO: rename filter string when refactoring the analysis reports.
      analysis_report.filter_string = self._event_filter_expression

    self._storage_writer.AddAnalysisReport(analysis_report)

    self.number_of_produced_analysis_reports += 1
    self.number_of_produced_event_tags = (
        self._storage_writer.number_of_event_tags)