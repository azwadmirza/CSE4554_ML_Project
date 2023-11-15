  def GetStorageInformation(self):
    """Retrieves storage (preprocessing) information stored in the storage file.

    Returns:
      A list of preprocessing objects (instances of PreprocessingObject)
      that contain the storage information.
    """
    stream_name = u'information.dump'
    if not self._HasStream(stream_name):
      return []

    data_stream = _SerializedDataStream(self._zipfile, self._path, stream_name)

    information = []
    preprocess_object = self._ReadPreprocessObject(data_stream)
    while preprocess_object:
      information.append(preprocess_object)
      preprocess_object = self._ReadPreprocessObject(data_stream)

    stores = self._GetSerializedEventObjectStreamNumbers()
    information[-1].stores = {}
    information[-1].stores[u'Number'] = len(stores)
    for store_number in stores:
      store_identifier = u'Store {0:d}'.format(store_number)
      information[-1].stores[store_identifier] = self._ReadMeta(store_number)

    return information