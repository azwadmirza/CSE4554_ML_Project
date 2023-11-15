    def __init__(self, config, **kwargs):
        """Initialise the historian.

        The historian makes two connections to the data store.  Both of
        these connections are available across the main and processing
        thread of the historian.  topic_map and topic_meta are used as
        cache for the meta data and topic maps.

        :param config: dictionary object containing the configurations for
                       this historian
        :param kwargs: additional keyword arguments. (optional identity and
                       topic_replace_list used by parent classes)
        """
        self.config = config
        self.topic_id_map = {}
        self.topic_name_map = {}
        self.topic_meta = {}
        self.agg_topic_id_map = {}
        self.tables_def = {}
        self.reader = None
        self.writer = None
        super(SQLHistorian, self).__init__(**kwargs)