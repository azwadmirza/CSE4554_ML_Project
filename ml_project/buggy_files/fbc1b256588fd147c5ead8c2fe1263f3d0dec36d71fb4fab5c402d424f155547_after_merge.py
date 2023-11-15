    def historian_setup(self):
        thread_name = threading.currentThread().getName()
        _log.debug("historian_setup on Thread: {}".format(thread_name))

        database_type = self.config['connection']['type']
        self.tables_def, table_names = self.parse_table_def(self.config)
        db_functs_class = sqlutils.get_dbfuncts_class(database_type)
        self.reader = db_functs_class(self.config['connection']['params'],
                                      table_names)
        self.writer = db_functs_class(self.config['connection']['params'],
                                      table_names)
        self.reader.setup_historian_tables()

        topic_id_map, topic_name_map = self.reader.get_topic_map()
        self.topic_id_map.update(topic_id_map)
        self.topic_name_map.update(topic_name_map)
        self.agg_topic_id_map = self.reader.get_agg_topic_map()