  def MergeAttributeContainers(
      self, callback=None, maximum_number_of_containers=0):
    """Reads attribute containers from a task storage file into the writer.

    Args:
      callback (function[StorageWriter, AttributeContainer]): function to call
          after each attribute container is deserialized.
      maximum_number_of_containers (Optional[int]): maximum number of
          containers to merge, where 0 represent no limit.

    Returns:
      bool: True if the entire task storage file has been merged.

    Raises:
      RuntimeError: if the add method for the active attribute container
          type is missing.
      OSError: if the task storage file cannot be deleted.
      ValueError: if the maximum number of containers is a negative value.
    """
    if maximum_number_of_containers < 0:
      raise ValueError('Invalid maximum number of containers')

    if not self._cursor:
      self._Open()
      self._ReadStorageMetadata()
      self._container_types = self._GetContainerTypes()

    number_of_containers = 0
    while self._active_cursor or self._container_types:
      if not self._active_cursor:
        self._PrepareForNextContainerType()

      if maximum_number_of_containers == 0:
        rows = self._active_cursor.fetchall()
      else:
        number_of_rows = maximum_number_of_containers - number_of_containers
        rows = self._active_cursor.fetchmany(size=number_of_rows)

      if not rows:
        self._active_cursor = None
        continue

      for row in rows:
        identifier = identifiers.SQLTableIdentifier(
            self._active_container_type, row[0])

        if self._compression_format == definitions.COMPRESSION_FORMAT_ZLIB:
          serialized_data = zlib.decompress(row[1])
        else:
          serialized_data = row[1]

        attribute_container = self._DeserializeAttributeContainer(
            self._active_container_type, serialized_data)
        attribute_container.SetIdentifier(identifier)

        if self._active_container_type == self._CONTAINER_TYPE_EVENT_TAG:
          event_identifier = identifiers.SQLTableIdentifier(
              self._CONTAINER_TYPE_EVENT,
              attribute_container.event_row_identifier)
          attribute_container.SetEventIdentifier(event_identifier)

          del attribute_container.event_row_identifier

        if callback:
          callback(self._storage_writer, attribute_container)

        self._add_active_container_method(
            attribute_container, serialized_data=serialized_data)

        number_of_containers += 1

      if (maximum_number_of_containers != 0 and
          number_of_containers >= maximum_number_of_containers):
        return False

    self._Close()

    os.remove(self._path)

    return True