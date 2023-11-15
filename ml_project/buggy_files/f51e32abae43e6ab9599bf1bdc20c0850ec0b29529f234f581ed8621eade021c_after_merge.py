    def update_server_list(self):
        for language in self.get_languages():
            config = {'status': self.STOPPED,
                      'config': self.get_language_config(language),
                      'instance': None}
            if language not in self.clients:
                self.clients[language] = config
                self.register_queue[language] = []
            else:
                logger.debug(
                    self.clients[language]['config'] != config['config'])
                current_config = self.clients[language]['config']
                new_config = config['config']
                restart_diff = ['cmd', 'args', 'host', 'port', 'external']
                restart = any([current_config[x] != new_config[x]
                               for x in restart_diff])
                if restart:
                    if self.clients[language]['status'] == self.STOPPED:
                        self.clients[language] = config
                    elif self.clients[language]['status'] == self.RUNNING:
                        self.close_client(language)
                        self.clients[language] = config
                        self.start_client(language)
                else:
                    if self.clients[language]['status'] == self.RUNNING:
                        client = self.clients[language]['instance']
                        client.send_plugin_configurations(
                            new_config['configurations'])