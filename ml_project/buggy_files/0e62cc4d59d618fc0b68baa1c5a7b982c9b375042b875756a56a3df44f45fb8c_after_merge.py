  def StoreReport(self, analysis_report):
    """Store an analysis report.

    Args:
      analysis_report: an analysis report object (instance of AnalysisReport).
    """
    report_number = 1
    for name in self._GetStreamNames():
      if name.startswith(u'plaso_report.'):
        _, _, number_string = name.partition(u'.')
        try:
          number = int(number_string, 10)
        except ValueError:
          logging.error(u'Unable to read in report number.')
          number = 0
        if number >= report_number:
          report_number = number + 1

    stream_name = u'plaso_report.{0:06}'.format(report_number)

    if self._serializers_profiler:
      self._serializers_profiler.StartTiming(u'analysis_report')

    serialized_report_proto = self._analysis_report_serializer.WriteSerialized(
        analysis_report)

    if self._serializers_profiler:
      self._serializers_profiler.StopTiming(u'analysis_report')

    self._WriteStream(stream_name, serialized_report_proto)