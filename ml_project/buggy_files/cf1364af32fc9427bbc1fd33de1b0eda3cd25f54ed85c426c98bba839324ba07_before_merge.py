    def update_stats_history(self):
        """Update stats history."""
        # If the plugin data is a dict, the dict's key should be used
        if self.get_key() is None:
            item_name = ''
        else:
            item_name = self.get_key()
        # Build the history
        if self.get_export() and self._history_enable():
            for i in self.get_items_history_list():
                if isinstance(self.get_export(), list):
                    # Stats is a list of data
                    # Iter throught it (for exemple, iter throught network
                    # interface)
                    for l in self.get_export():
                        self.stats_history.add(
                            str(l[item_name]) + '_' + i['name'],
                            l[i['name']],
                            description=i['description'],
                            history_max_size=self._limits['history_size'])
                else:
                    # Stats is not a list
                    # Add the item to the history directly
                    self.stats_history.add(i['name'],
                                           self.get_export()[i['name']],
                                           description=i['description'],
                                           history_max_size=self._limits['history_size'])