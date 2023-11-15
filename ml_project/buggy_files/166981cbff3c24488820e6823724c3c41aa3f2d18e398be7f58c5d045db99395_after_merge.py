  def Open(self):
    """Opens the plaso storage file."""
    pre_obj = event.PreprocessObject()
    pre_obj.collection_information = {
        u'time_of_run': timelib.Timestamp.GetNow()}

    filter_expression = self._output_mediator.filter_expression
    if filter_expression:
      pre_obj.collection_information[u'filter'] = filter_expression

    storage_file_path = self._output_mediator.storage_file_path
    if storage_file_path:
      pre_obj.collection_information[u'file_processed'] = storage_file_path

    self._storage_file = zip_file.StorageFile(self._file_path, pre_obj=pre_obj)