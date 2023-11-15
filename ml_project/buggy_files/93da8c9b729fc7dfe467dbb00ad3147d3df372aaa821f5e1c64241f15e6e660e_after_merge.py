def historian(config_path, **kwargs):

    config = utils.load_config(config_path)
    connection = config.get('connection', None);

    assert connection is not None
    databaseType = connection.get('type', None)
    assert databaseType is not None
    params = connection.get('params', None)
    assert params is not None
    identity = config.get('identity', kwargs.pop('identity', None))

    if databaseType == 'sqlite':
        from .db.sqlitefuncts import SqlLiteFuncts as DbFuncts
    elif databaseType == 'mysql':
        from .db.mysqlfuncts import MySqlFuncts as DbFuncts
    else:
        _log.error("Unknown database type specified!")
        raise Exception("Unkown database type specified!")
        
    class SQLHistorian(BaseHistorian):
        '''This is a simple example of a historian agent that writes stuff
        to a SQLite database. It is designed to test some of the functionality
        of the BaseHistorianAgent.
        '''

        @Core.receiver("onstart")
        def starting(self, sender, **kwargs):
            
            print('Starting address: {} identity: {}'.format(self.core.address, self.core.identity))
            try:
                self.reader = DbFuncts(**connection['params'])
            except AttributeError:
                _log.exception('bad connection parameters')
                self.core.stop()
                return
                        
            self.topic_map = self.reader.get_topic_map()

            if self.core.identity == 'platform.historian':
                # Check to see if the platform agent is available, if it isn't then
                # subscribe to the /platform topic to be notified when the platform
                # agent becomes available.
                try:
                    ping = self.vip.ping('platform.agent',
                                         'awake?').get(timeout=3)
                    _log.debug("Ping response was? "+ str(ping))
                    self.vip.rpc.call('platform.agent', 'register_service',
                                      self.core.identity).get(timeout=3)
                except Unreachable:
                    _log.debug('Could not register historian service')
                finally:
                    self.vip.pubsub.subscribe('pubsub', '/platform',
                                              self.__platform)
                    _log.debug("Listening to /platform")

        def __platform(self, peer, sender, bus, topic, headers, message):
            _log.debug('Platform is now: {}'.format(message))
            if message == 'available' and \
                    self.core.identity == 'platform.historian':
                gevent.spawn(self.vip.rpc.call, 'platform.agent', 'register_service',
                                   self.core.identity)
                gevent.sleep(0)

        def publish_to_historian(self, to_publish_list):
            _log.debug("publish_to_historian number of items: {}"
                       .format(len(to_publish_list)))
            
            # load a topic map if there isn't one yet.
            try:
                self.topic_map.items()
            except:
                self.topic_map = self.reader.get_topic_map()

            for x in to_publish_list:
                ts = x['timestamp']
                topic = x['topic']
                value = x['value']
                # look at the topics that are stored in the database already
                # to see if this topic has a value
                topic_id = self.topic_map.get(topic)

                if topic_id is None:
                    row  = self.writer.insert_topic(topic)
                    topic_id = row[0]
                    self.topic_map[topic] = topic_id

                self.writer.insert_data(ts,topic_id, value)

            _log.debug('published {} data values:'.format(len(to_publish_list)))
            self.report_all_published()

        def query_topic_list(self):
            if len(self.topic_map) > 0:
                return self.topic_map.keys()
            else:
                # No topics present.
                return []

        def query_historian(self, topic, start=None, end=None, skip=0,
                            count=None, order="FIRST_TO_LAST"):
            """This function should return the results of a query in the form:
            {"values": [(timestamp1, value1), (timestamp2, value2), ...],
             "metadata": {"key1": value1, "key2": value2, ...}}

             metadata is not required (The caller will normalize this to {} for you)
            """
            return self.reader.query(topic, start=start, end=end, skip=skip,
                                     count=count, order=order)

        def historian_setup(self):
            try:
                self.writer = DbFuncts(**connection['params'])
            except AttributeError as exc:
                print(exc)
                self.core.stop()

    SQLHistorian.__name__ = 'SQLHistorian'
    return SQLHistorian(identity=identity, **kwargs)