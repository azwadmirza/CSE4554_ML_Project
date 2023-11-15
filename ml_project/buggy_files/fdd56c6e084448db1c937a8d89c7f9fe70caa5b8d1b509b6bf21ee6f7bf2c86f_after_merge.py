    def _initialize_notified_handlers(self, play):
        '''
        Clears and initializes the shared notified handlers dict with entries
        for each handler in the play, which is an empty array that will contain
        inventory hostnames for those hosts triggering the handler.
        '''

        # Zero the dictionary first by removing any entries there.
        # Proxied dicts don't support iteritems, so we have to use keys()
        self._notified_handlers.clear()
        self._listening_handlers.clear()

        def _process_block(b):
            temp_list = []
            for t in b.block:
                if isinstance(t, Block):
                    temp_list.extend(_process_block(t))
                else:
                    temp_list.append(t)
            return temp_list

        handler_list = []
        for handler_block in play.handlers:
            handler_list.extend(_process_block(handler_block))
        # then initialize it with the given handler list
        self.update_handler_list(handler_list)