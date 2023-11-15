    def on_task_input(self, task, config):
        entries = self._get_watchlist_entries(task, config)
        entries += self._get_favorites_entries(task, config)

        return entries