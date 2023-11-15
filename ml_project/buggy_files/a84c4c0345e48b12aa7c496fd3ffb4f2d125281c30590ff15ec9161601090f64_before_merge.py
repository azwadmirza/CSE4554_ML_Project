    def _get_system_stats(self):
        with ConnectTo(StatisticDbViewer, self._config) as stats_db:
            backend_data = stats_db.get_statistic("backend")

        return {
            'backend_cpu_percentage': backend_data['system']['cpu_percentage'],
            'number_of_running_analyses': len(backend_data['analysis']['current_analyses'])
        }