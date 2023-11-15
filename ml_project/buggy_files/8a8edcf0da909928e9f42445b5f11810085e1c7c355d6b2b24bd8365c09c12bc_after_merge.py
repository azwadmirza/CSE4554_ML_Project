    def __init__(self, filename, filename_info, filetype_info,
                 engine=None):
        """Init the file handler."""
        super(NCOLCIChannelBase, self).__init__(filename, filename_info,
                                                filetype_info)

        self.channel = filename_info.get('dataset_name')