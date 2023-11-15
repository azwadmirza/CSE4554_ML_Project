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