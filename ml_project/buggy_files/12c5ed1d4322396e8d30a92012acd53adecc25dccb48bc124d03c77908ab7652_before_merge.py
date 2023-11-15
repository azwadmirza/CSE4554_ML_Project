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
        super(SQLHistorian, self).__init__(**kwargs)
        database_type = config['connection']['type']
        self.tables_def, table_names = self.parse_table_def(config)
        db_functs_class = sqlutils.get_dbfuncts_class(database_type)
        self.reader = db_functs_class(config['connection']['params'],
                                      table_names)
        self.writer = db_functs_class(config['connection']['params'],
                                      table_names)
        self.reader.setup_historian_tables()

        self.topic_id_map = {}
        self.topic_name_map = {}
        self.topic_meta = {}
        self.agg_topic_id_map = {}