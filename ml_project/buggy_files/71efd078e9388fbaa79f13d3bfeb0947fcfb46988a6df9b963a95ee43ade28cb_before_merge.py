  def __init__(self, input_reader=None, output_writer=None):
    """Initializes the CLI tool object.

    Args:
      input_reader: optional input reader (instance of InputReader).
                    The default is None which indicates the use of the stdin
                    input reader.
      output_writer: optional output writer (instance of OutputWriter).
                     The default is None which indicates the use of the stdout
                     output writer.
    """
    super(PregTool, self).__init__(
        input_reader=input_reader, output_writer=output_writer)
    self._front_end = preg.PregFrontend()
    self._key_path = None
    self._knowledge_base_object = knowledge_base.KnowledgeBase()
    self._parse_restore_points = False
    self._path_resolvers = []
    self._verbose_output = False
    self._windows_directory = u''

    self.plugin_names = u''
    self.registry_file = u''
    self.run_mode = None
    self.source_type = None