    def __init__(self, parent=None):
        super(RemoteTableModel, self).__init__(parent)
        # Unique identifier mapping for items. For torrents, it is infohash and for channels, it is concatenated value
        # of public key and channel id
        self.item_uid_map = {}

        self.data_items = []
        self.item_load_batch = 50
        self.sort_by = self.columns[self.default_sort_column] if self.default_sort_column >= 0 else None
        self.sort_desc = True
        self.saved_header_state = None
        self.saved_scroll_state = None

        # Every remote query must be attributed to its specific model to avoid updating wrong models
        # on receiving a result. We achieve this by maintaining a set of in-flight remote queries.
        # Note that this only applies to results that are returned through the events notification
        # mechanism, because REST requests attribution is maintained by the RequestManager.
        # We do not clean it up after receiving a result because we don't know if the result was the
        # last one. In a sense, the queries' UUIDs play the role of "subscription topics" for the model.
        self.remote_queries = set()