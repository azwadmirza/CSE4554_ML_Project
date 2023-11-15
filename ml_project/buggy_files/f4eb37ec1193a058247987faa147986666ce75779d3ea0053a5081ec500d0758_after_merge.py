    def __init__(self, filename, filename_info, filetype_info):
        """Initialize the reader."""

        self.filename = filename
        self.platform_name = None
        self.available_channels = {}
        self.channel_order_list = []
        for item in CHANNEL_LIST:
            self.available_channels[item] = False

        self._get_header()

        for item in CHANNEL_LIST:
            if self.available_channels.get(item):
                self.channel_order_list.append(item)

        self.memmap = self._get_memmap()