    def _strategy_simple(self, status_list, tasks, *args, kind=None, **kwargs):
        self._general_strategy(status_list, tasks, *args, strategy_type='simple', kind=None, **kwargs)