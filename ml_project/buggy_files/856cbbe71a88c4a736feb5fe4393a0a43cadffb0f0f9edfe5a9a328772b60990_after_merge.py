  def __init__(self):
    """Initializes the front-end object."""
    super(PsortFrontend, self).__init__()

    self._analysis_process_info = []
    self._data_location = None
    self._filter_buffer = None
    self._filter_expression = None
    self._filter_object = None
    self._output_filename = None
    self._output_file_object = None
    self._output_format = None
    self._preferred_language = u'en-US'
    self._quiet_mode = False
    self._storage_file = None