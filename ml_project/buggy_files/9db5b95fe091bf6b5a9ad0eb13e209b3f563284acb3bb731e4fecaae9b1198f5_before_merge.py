  def CompileReport(self, mediator):
    """Compiles an analysis report.

    Args:
      mediator (AnalysisMediator): mediates interactions between
          analysis plugins and other components, such as storage and dfvfs.

    Returns:
      AnalysisReport: report.
    """
    tags = []
    lines_of_text = [u'{0:s} hash tagging Results'.format(self.NAME)]
    while self._ContinueReportCompilation():
      try:
        self._LogProgressUpdateIfReasonable()
        hash_analysis = self.hash_analysis_queue.get(
            timeout=self._analysis_queue_timeout)
      except Queue.Empty:
        # The result queue is empty, but there could still be items that need
        # to be processed by the analyzer.
        continue
      pathspecs, labels, new_tags = self._HandleHashAnalysis(
          hash_analysis)
      tags.extend(new_tags)
      if labels:
        for pathspec in pathspecs:
          text_line = self._GenerateTextLine(mediator, pathspec, labels)
          lines_of_text.append(text_line)

    self._analyzer.SignalAbort()

    lines_of_text.append(u'')
    report_text = u'\n'.join(lines_of_text)
    analysis_report = reports.AnalysisReport(
        plugin_name=self.NAME, text=report_text)
    analysis_report.SetTags(tags)
    return analysis_report