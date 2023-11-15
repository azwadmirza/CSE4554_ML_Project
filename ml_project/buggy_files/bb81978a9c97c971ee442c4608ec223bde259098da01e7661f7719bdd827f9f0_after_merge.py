  def WorkersRunning(self):
    """Determines if the workers are running."""
    for extraction_worker_status in iter(self._extraction_workers.values()):
      if (extraction_worker_status.status ==
          definitions.PROCESSING_STATUS_COMPLETED):
        logging.debug(u'Worker completed.')
        continue
      if (extraction_worker_status.number_of_events_delta > 0 or
          extraction_worker_status.consumed_number_of_path_specs_delta > 0 or
          extraction_worker_status.produced_number_of_path_specs_delta > 0 or
          (extraction_worker_status.status ==
           definitions.PROCESSING_STATUS_HASHING)):
        return True

    return False