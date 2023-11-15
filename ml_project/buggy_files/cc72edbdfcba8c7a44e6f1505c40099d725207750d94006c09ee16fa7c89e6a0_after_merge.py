  def _SetSerializerFormat(self, serializer_format):
    """Set the serializer format.

    Args:
      serializer_format: the storage serializer format.

    Raises:
      ValueError: if the serializer format is not supported.
    """
    if serializer_format == definitions.SERIALIZER_FORMAT_JSON:
      self._serializer_format_string = u'json'

      self._analysis_report_serializer = (
          json_serializer.JSONAnalysisReportSerializer)
      self._event_object_serializer = (
          json_serializer.JSONEventObjectSerializer)
      self._event_tag_serializer = (
          json_serializer.JSONEventTagSerializer)
      self._pre_obj_serializer = (
          json_serializer.JSONPreprocessObjectSerializer)

    elif serializer_format == definitions.SERIALIZER_FORMAT_PROTOBUF:
      self._serializer_format_string = u'proto'

      self._analysis_report_serializer = (
          protobuf_serializer.ProtobufAnalysisReportSerializer)
      self._event_object_serializer = (
          protobuf_serializer.ProtobufEventObjectSerializer)
      self._event_tag_serializer = (
          protobuf_serializer.ProtobufEventTagSerializer)
      self._pre_obj_serializer = (
          protobuf_serializer.ProtobufPreprocessObjectSerializer)

    else:
      raise ValueError(
          u'Unsupported serializer format: {0:s}'.format(serializer_format))