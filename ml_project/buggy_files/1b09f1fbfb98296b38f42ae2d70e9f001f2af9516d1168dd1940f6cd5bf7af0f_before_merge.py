    def __init__(self,
                 config_files,
                 filter_parameters=None,
                 filter_filenames=True,
                 **kwargs):
        super(FileYAMLReader, self).__init__(config_files)

        self.file_handlers = {}
        self.filter_filenames = self.info.get('filter_filenames', filter_filenames)
        self.filter_parameters = filter_parameters or {}
        if kwargs:
            logger.warning("Unrecognized/unused reader keyword argument(s) '{}'".format(kwargs))