  def CompileReport(self, mediator):
    """Compiles an analysis report.

    Args:
      mediator (AnalysisMediator): mediates interactions between
          analysis plugins and other components, such as storage and dfvfs.

    Returns:
      AnalysisReport: report.
    """
    # TODO: refactor to update the counter on demand instead of
    # during reporting.
    path_specs_per_labels_counter = collections.Counter()
    tags = []
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
      for label in labels:
        path_specs_per_labels_counter[label] += len(pathspecs)

    self._analyzer.SignalAbort()

    lines_of_text = [u'{0:s} hash tagging results'.format(self.NAME)]
    for label, count in path_specs_per_labels_counter.items():
      line_of_text = (
          u'{0:d} path specifications tagged with label: {1:s}'.format(
              count, label))
      lines_of_text.append(line_of_text)
    lines_of_text.append(u'')
    report_text = u'\n'.join(lines_of_text)

    analysis_report = reports.AnalysisReport(
        plugin_name=self.NAME, text=report_text)
    analysis_report.SetTags(tags)
    return analysis_report